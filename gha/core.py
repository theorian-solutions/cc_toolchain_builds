from typing import (
    Any,
    Generic,
    List,
    Literal,
    Tuple,
    TypeVar,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from pydantic import AliasGenerator, BaseModel, ConfigDict


class GhaModel(BaseModel):
    """Base model for GitHub Action entities."""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            serialization_alias=lambda field_name: field_name.replace("_", "-"),
        )
    )


T = TypeVar("T")


class GhaComplexDecorator:
    def __init__(self, field: Tuple[str, Any], *parents: List[Tuple[str, Any]]):
        attributes = {
            k: GhaComplexDecorator._get_optional_arg(v)
            for k, v in get_type_hints(field[1]).items()
        }
        self.complex = {
            k: GhaComplexDecorator((k, v), field, *parents)
            for k, v in attributes.items()
            if not GhaComplexDecorator._is_primitive(v)
        }
        self.primitives = {
            k: v for k, v in attributes.items() if GhaComplexDecorator._is_primitive(v)
        }

    @staticmethod
    def _is_optional_type(annotation):
        """Checks if given type is Optional."""
        origin = get_origin(annotation)
        args = get_args(annotation)
        return origin is Union and type(None) in args

    @staticmethod
    def _get_optional_arg(annotation):
        """If given type is optional, returns underlying type or propagates given type."""
        if GhaComplexDecorator._is_optional_type(annotation):
            return get_args(annotation)[0]
        return annotation

    @staticmethod
    def _is_primitive(annotation):
        primitive_types = (
            int,
            float,
            str,
            bool,
            bytes,
            complex,
            type(None),
            dict,
            list,
            Literal,
        )

        annotations_to_check = [annotation]

        if annotation is Union:
            annotations_to_check = get_args(annotation)

        return all(
            a in primitive_types or get_origin(a) in primitive_types
            for a in annotations_to_check
        )


class GhaDecorator(Generic[T], GhaComplexDecorator):
    def __init__(self, *discarded_attributes: List[str]):
        GhaComplexDecorator.__init__(self, ("", get_args(self.__orig_bases__[0])[0]))

        self.complex = {
            k: v for k, v in self.complex.items() if not k in discarded_attributes
        }
        self.primitives = {
            k: v for k, v in self.primitives.items() if not k in discarded_attributes
        }

    # def __getattr__(self, name):
    #     if name not in self._marks:
    #         self._marks[name] = self._create_mark(name)
    #     return self._marks[name]

    # def _create_mark(self, name):
    #     def mark_decorator(func):
    #         if not hasattr(func, "_marks"):
    #             func._marks = []
    #         func._marks.append(name)
    #         return func

    #     return mark_decorator

    # def get_marks(self, func):
    #     return getattr(func, "_marks", [])
