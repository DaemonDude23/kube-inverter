#!/usr/bin/env python3
import argparse
import logging
from pathlib import Path
from sys import stdout

from ruamel.yaml import YAML


def check_path_types(arguments):
    if arguments.path_type is not None:
        # validate pathType's value (if overridden)
        list_path_types = ["Exact", "Prefix", "ImplementationSpecific"]
        bool_valid_prefix_found = False
        for path_type in list_path_types:  # loop through available options
            if arguments.path_type == path_type:
                bool_valid_prefix_found = True
                break  # bail once we confirm the argument given matches one of three expected values
        if not bool_valid_prefix_found:
            logging.debug(f"Invalid Ingress pathType provided ('{arguments.path_type}') - Exiting")


def init_arg_parser():
    try:
        parser = argparse.ArgumentParser(
            prog="kube-inverter",
            description="converts Kubernetes Ingress objects from 'networking.k8s.io/v1beta1' to 'networking.k8s.io/v1'",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )

        args = parser.add_argument_group()
        args.add_argument(
            "--debug",
            dest="debug",
            action="store_true",
            help="enable debug logging",
            default=False,
        )
        args.add_argument(
            "--output-file",
            "-o",
            dest="output_file",
            action="store",
            help="output file path. This disables an in-place update to the input file",
        )
        args.add_argument(
            "--path-type",
            "--pathType",
            "-p",
            dest="path_type",
            action="store",
            help="path Type for Ingress rule. Options: 'Exact', 'ImplementationSpecific', 'Prefix'",
        )
        args.add_argument("--version", "-v", action="version", version="v0.2.0")
        args.add_argument("input_file", action="store", type=str, help="input file")
        arguments = parser.parse_args()

        if arguments.debug:
            logging.basicConfig(
                level=logging.DEBUG,
                datefmt=None,
                stream=stdout,
                format="[%(asctime)s %(levelname)s] %(message)s",
            )
        else:
            logging.basicConfig(
                level=logging.INFO,
                datefmt=None,
                stream=stdout,
                format="[%(asctime)s %(levelname)s] %(message)s",
            )

        return arguments
    except argparse.ArgumentError as e:
        logging.error("Error parsing arguments")
        raise e


def convert(arguments):
    input_file_path = Path(arguments.input_file)
    # write to separate output file
    if arguments.output_file:
        output_file_path = Path(arguments.output_file)
        ingress_yaml_file = output_file_path.with_suffix(".tmp")
    # create temp file to only overwrite input
    else:
        ingress_yaml_file = input_file_path.with_suffix(".tmp")

    # prepare counters
    int_num_of_documents = int()
    int_num_of_ingress_v1beta_documents = int()
    int_num_of_ingress_v1beta_converted = int()
    int_num_of_ingress_v1_documents = int()

    with YAML(output=ingress_yaml_file) as yaml:
        # yaml config defaults
        yaml.indent()
        yaml.preserve_quotes = True
        yaml.preserve_comments = True

        # loop through each YAML document
        for data in yaml.load_all(input_file_path):
            int_num_of_documents += 1

            # ensure we're migrating from the correct apiVersion
            try:
                # v1
                if data["kind"] == "Ingress" and data["apiVersion"] == "networking.k8s.io/v1":
                    int_num_of_ingress_v1_documents += 1

                # v1beta1
                if data["kind"] == "Ingress" and data["apiVersion"] == "networking.k8s.io/v1beta1":
                    int_num_of_ingress_v1beta_documents += 1
                    data["apiVersion"] = "networking.k8s.io/v1"  # bulldoze apiVersion from input

                    # defaultBackend - if a 'backend' is defined, rename it to 'defaultBackend'
                    try:
                        if data["spec"]["backend"]:
                            data["spec"]["defaultBackend"] = data["spec"]["backend"]
                            del data["spec"]["backend"]
                    except KeyError:
                        logging.debug("'spec.backend' not found in object. That is okay.")

                    try:  # service name
                        str_service_name = data["spec"]["defaultBackend"]["serviceName"]
                        del data["spec"]["defaultBackend"]["serviceName"]
                        logging.debug(f"Found serviceName: {str_service_name}")
                        data["spec"]["defaultBackend"]["service"] = {"name": str_service_name}
                    except KeyError:
                        logging.debug("Document is missing the serviceName in its rules. That is okay.")

                    try:  # servicePort
                        service_port = data["spec"]["defaultBackend"]["servicePort"]
                        del data["spec"]["defaultBackend"]["servicePort"]

                        try:  # service.port.number
                            data["spec"]["defaultBackend"]["service"]["port"] = {"number": int(service_port)}
                            logging.debug(f"Found servicePort (number): {service_port}")
                        except ValueError:  # service.port.name
                            logging.debug(f"Found servicePort (name): {service_port}")
                            data["spec"]["defaultBackend"]["service"]["port"] = {"name": str(service_port)}

                    except KeyError:
                        logging.debug("Document is missing the ServicePort in its rules. That is okay.")

                    # rules
                    for rule in data["spec"]["rules"]:
                        for a_path in rule["http"]["paths"]:
                            if arguments.path_type is not None:
                                a_path["pathType"] = arguments.path_type

                            try:  # service name
                                str_service_name = a_path["backend"]["serviceName"]
                                del a_path["backend"]["serviceName"]
                                logging.debug(f"Found serviceName: {str_service_name}")
                                a_path["backend"]["service"] = {"name": str_service_name}
                            except KeyError:
                                logging.debug("Document is missing the serviceName in its rules. That is okay.")

                            try:  # servicePort
                                service_port = a_path["backend"]["servicePort"]
                                del a_path["backend"]["servicePort"]

                                try:  # service.port.number
                                    a_path["backend"]["service"]["port"] = {"number": int(service_port)}
                                    logging.debug(f"Found servicePort (number): {service_port}")
                                except ValueError:  # service.port.name
                                    logging.debug(f"Found servicePort (name): {service_port}")
                                    a_path["backend"]["service"]["port"] = {"name": str(service_port)}

                            except KeyError:
                                logging.debug("Document is missing the serviceName in its rules. That is okay.")
                    int_num_of_ingress_v1beta_converted += 1

            except KeyError as e:
                logging.warning(f"{input_file_path} - Failed to find expected keys in input YAML")

            yaml.dump(data)  # write updates to payload

    logging.info(f"{input_file_path} - Number of documents found: {int_num_of_documents}")
    logging.info(f"{input_file_path} - Number of v1beta Ingress documents found: {int_num_of_ingress_v1beta_documents}")
    logging.info(f"{input_file_path} - Number of v1beta Ingress documents converted to v1: {int_num_of_ingress_v1beta_converted}")
    logging.info(f"{input_file_path} - Number of v1 Ingress documents found: {int_num_of_ingress_v1_documents}")

    if arguments.output_file:
        ingress_yaml_file.rename(output_file_path)
    else:
        input_file_path.unlink()
        ingress_yaml_file.rename(input_file_path)


def main():
    arguments = init_arg_parser()
    if arguments.path_type is not None:
        check_path_types(arguments)
    convert(arguments)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt or SystemExit:
        exit(1)
