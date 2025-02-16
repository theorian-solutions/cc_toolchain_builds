from abc import ABC, abstractmethod
import argparse
import logging
import os
import sys
from typing import (
    Generic,
    List,
    Literal,
    TypeVar,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

import docker

from github import Auth, Github

TCliArgs = TypeVar("TCliArgs")


class CliApp(ABC, Generic[TCliArgs]):
    def __init__(self, name: str):
        self._Model = get_args(self.__orig_bases__[0])[0]
        self._app_name = name
        self._docker = None
        self._github = None
        self._setup_logger()
        self._parse_args()

    def _setup_logger(self):
        """Utility function to initialize logger."""
        self._logger = logging.getLogger(self._app_name)
        self._logger.setLevel(level=logging.INFO)

        # Create a StreamHandler to log to stdout
        stream_handler = logging.StreamHandler(sys.stdout)

        # Create a formatter and set it to the handler
        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s]: %(message)s")
        stream_handler.setFormatter(formatter)

        # Add the handler to the logger
        self._logger.addHandler(stream_handler)

    def _parse_args(self):
        """Utility function to parse CLI arguments."""

        parser = argparse.ArgumentParser(description=self._Model.__doc__)
        for field_name, field_type in get_type_hints(self._Model).items():
            field_info = self._Model.__fields__[field_name]
            arg_name = f'--{field_name.replace("_", "-")}'

            field_type_origin = get_origin(field_type)
            field_type_args = get_args(field_type)
            required = True
            nargs = None

            if (
                field_type_origin is Union
                and len(field_type_args) == 2
                and type(None) in field_type_args
            ):
                # Handle optional type
                inner_type = next(
                    a_type for a_type in field_type_args if a_type != type(None)
                )
                field_type_origin = get_origin(inner_type)
                field_type_args = get_args(inner_type)
                required = False

            if field_type_origin in (List, list):
                # Handle list case

                inner_type = field_type_args[0]
                field_type_origin = get_origin(inner_type)
                field_type_args = get_args(inner_type)
                nargs = "+" if required else "*"

            if field_type_origin is Literal:
                # Handle literal choices

                parser.add_argument(
                    arg_name,
                    type=str,
                    choices=field_type_args,
                    help=field_info.description,
                    required=required,
                    nargs=nargs,
                )
            elif field_type_origin is bool:
                # Handle bool type

                parser.add_argument(
                    arg_name,
                    type=str,
                    choices=["yes", "no"],
                    help=field_info.description,
                    required=required,
                    nargs=nargs,
                )
            else:
                # Handle any other type

                parser.add_argument(
                    arg_name,
                    type=field_type_origin,
                    help=field_info.description,
                    required=required,
                    nargs=nargs,
                )

        self._args = self._Model.model_validate(vars(parser.parse_args()))

    @property
    def logger(self) -> logging.Logger:
        """Gets the application logger."""
        return self._logger

    @property
    def args(self) -> TCliArgs:
        """Gets provided CLI arguments."""
        return self._args

    @property
    def docker(self) -> docker.DockerClient:
        if self._docker is None:
            self._docker = docker.from_env()
        return self._docker

    @property
    def github(self) -> Github:
        if self._github is None:
            if "GITHUB_TOKEN" not in os.environ:
                raise EnvironmentError("Environment variable 'GITHUB_TOKEN' not set!")
            auth = Auth.Token(os.environ["GITHUB_TOKEN"])
            self._github = Github(auth=auth)
        return self._github

    @abstractmethod
    def run(self):
        """Runs the CLI application logic."""
        pass

    @classmethod
    def exec(cls, module_name: str):
        """Runs the application logic if current module is main."""
        if module_name == "__main__":
            cls().run()
