"""Custom-op schema compatibility for torch-directml's PyTorch 2.4.1."""

import typing

import torch


def enable_schema_compatibility():
    if torch.__version__.split("+")[0] != "2.4.1":
        return

    # PyTorch 2.4.1 recognizes typing.List but not the equivalent list[T]
    # annotations used by current comfy-kitchen custom ops.
    from torch._library.infer_schema import SUPPORTED_PARAM_TYPES, SUPPORTED_RETURN_TYPES
    import torch._custom_op.impl as custom_op_impl

    for table in (SUPPORTED_PARAM_TYPES, SUPPORTED_RETURN_TYPES):
        for annotation, schema in list(table.items()):
            if typing.get_origin(annotation) is list:
                table[list[typing.get_args(annotation)[0]]] = schema

    original_infer_schema = custom_op_impl.infer_schema

    def infer_schema(function, mutates_args=()):
        # PyTorch 2.4.1 also predates support for postponed annotations.
        function.__annotations__ = typing.get_type_hints(function)
        if function.__annotations__.get("return") is type(None):
            function.__annotations__["return"] = None
        return original_infer_schema(function, mutates_args)

    custom_op_impl.infer_schema = infer_schema


enable_schema_compatibility()
