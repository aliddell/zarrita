import functools
from typing import TYPE_CHECKING, Any, Dict, Literal, Tuple, Union

from cattr import Converter

if TYPE_CHECKING:
    pass


ZARR_JSON = "zarr.json"

BytesLike = Union[bytes, bytearray, memoryview]
ChunkCoords = Tuple[int, ...]
SliceSelection = Tuple[slice, ...]
Selection = Union[slice, SliceSelection]


def make_cattr():
    from zarrita.metadata import (
        BloscCodecMetadata,
        ChunkKeyEncodingMetadata,
        CodecMetadata,
        DefaultChunkKeyEncodingMetadata,
        EndianCodecMetadata,
        GzipCodecMetadata,
        ShardingCodecMetadata,
        TransposeCodecMetadata,
        V2ChunkKeyEncodingMetadata,
    )

    dataset_converter = Converter()

    def _structure_chunk_key_encoding_metadata(
        d: Dict[str, Any], _t
    ) -> ChunkKeyEncodingMetadata:
        if d["name"] == "default":
            return dataset_converter.structure(d, DefaultChunkKeyEncodingMetadata)
        if d["name"] == "v2":
            return dataset_converter.structure(d, V2ChunkKeyEncodingMetadata)
        raise KeyError

    dataset_converter.register_structure_hook(
        ChunkKeyEncodingMetadata, _structure_chunk_key_encoding_metadata
    )

    def _structure_codec_metadata(d: Dict[str, Any], _t=None) -> CodecMetadata:
        if d["name"] == "blosc":
            return dataset_converter.structure(d, BloscCodecMetadata)
        if d["name"] == "endian":
            return dataset_converter.structure(d, EndianCodecMetadata)
        if d["name"] == "transpose":
            return dataset_converter.structure(d, TransposeCodecMetadata)
        if d["name"] == "gzip":
            return dataset_converter.structure(d, GzipCodecMetadata)
        if d["name"] == "sharding_indexed":
            return dataset_converter.structure(d, ShardingCodecMetadata)
        raise KeyError

    dataset_converter.register_structure_hook(CodecMetadata, _structure_codec_metadata)

    dataset_converter.register_structure_hook_factory(
        lambda t: str(t) == "ForwardRef('CodecMetadata')",
        lambda t: _structure_codec_metadata,
    )

    def _structure_order(d: Any, _t=None) -> Union[Literal["C", "F"], Tuple[int, ...]]:
        if d == "C":
            return "C"
        if d == "F":
            return "F"
        if isinstance(d, list):
            return tuple(d)
        raise KeyError

    dataset_converter.register_structure_hook_factory(
        lambda t: str(t)
        == "typing.Union[typing.Literal['C', 'F'], typing.Tuple[int, ...]]",
        lambda t: _structure_order,
    )

    return dataset_converter


def product(tup: ChunkCoords) -> int:
    return functools.reduce(lambda x, y: x * y, tup, 1)
