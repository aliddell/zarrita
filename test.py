import zarrita
import numpy as np
import webknossos as wk

from zarrita.sharding import morton_order_iter


def test_sharding():
    from timeit import default_timer as timer

    # ds = wk.Dataset.open_remote(
    #     "l4_sample",
    #     organization_id="scalable_minds",
    #     webknossos_url="https://webknossos.org",
    # )
    ds = wk.Dataset.open(
        "/Users/norman/scalableminds/webknossos/binaryData/sample_organization/l4_sample"
    )

    def copy(data, path):
        s = zarrita.FileSystemStore("file://./testdata")
        a = zarrita.Array.create(
            s,
            path,
            shape=data.shape,
            chunk_shape=(512, 512, 512),
            dtype=data.dtype,
            fill_value=0,
            codecs=[
                zarrita.ShardingCodecMetadata(
                    configuration=zarrita.ShardingCodecConfigurationMetadata(
                        chunk_shape=(32, 32, 32),
                        codecs=[
                            zarrita.TransposeCodecMetadata(
                                configuration=zarrita.TransposeCodecConfigurationMetadata(
                                    order="F"
                                )
                            ),
                            zarrita.BloscCodecMetadata(
                                configuration=zarrita.BloscCodecConfigurationMetadata()
                            ),
                        ],
                    )
                ),
            ],
        )

        start = timer()
        a[:, :, :] = data
        print("WRITE", timer() - start)

        start = timer()
        read_data = a[:, :, :]
        print("READ", timer() - start)

        assert np.array_equal(data, read_data)

    copy(ds.get_layer("color").get_mag(1).read()[0], "l4_sample/color/1")
    # copy(ds.get_layer("segmentation").get_mag(1).read()[0], "l4_sample/segmentation/1")


def test_order_F():
    data = np.arange(0, 256, dtype="uint16").reshape((16, 16), order="F")

    s = zarrita.FileSystemStore("file://./testdata")
    a = zarrita.Array.create(
        s,
        "order_F",
        shape=data.shape,
        chunk_shape=(16, 16),
        dtype=data.dtype,
        fill_value=0,
        codecs=[
            zarrita.TransposeCodecMetadata(
                configuration=zarrita.TransposeCodecConfigurationMetadata(order="F")
            ),
        ],
    )

    a[:, :] = data
    read_data = a[:, :]
    assert np.array_equal(data, read_data)
    assert read_data.flags["F_CONTIGUOUS"]
    assert not read_data.flags["C_CONTIGUOUS"]


def test_order_C():
    data = np.arange(0, 256, dtype="uint16").reshape((16, 16), order="C")

    s = zarrita.FileSystemStore("file://./testdata")
    a = zarrita.Array.create(
        s,
        "order_C",
        shape=data.shape,
        chunk_shape=(16, 16),
        dtype=data.dtype,
        fill_value=0,
        codecs=[
            zarrita.TransposeCodecMetadata(
                configuration=zarrita.TransposeCodecConfigurationMetadata(order="C")
            ),
        ],
    )

    a[:, :] = data
    read_data = a[:, :]
    assert np.array_equal(data, read_data)
    assert read_data.flags["C_CONTIGUOUS"]
    assert not read_data.flags["F_CONTIGUOUS"]


def test_order_implicitC():
    data = np.arange(0, 256, dtype="uint16").reshape((16, 16), order="F")

    s = zarrita.FileSystemStore("file://./testdata")
    a = zarrita.Array.create(
        s,
        "order_implicitC",
        shape=data.shape,
        chunk_shape=(16, 16),
        dtype=data.dtype,
        fill_value=0,
    )

    a[:, :] = data
    read_data = a[:, :]
    assert np.array_equal(data, read_data)
    assert read_data.flags["C_CONTIGUOUS"]
    assert not read_data.flags["F_CONTIGUOUS"]


def test_open():
    s = zarrita.FileSystemStore("file://./testdata")
    a = zarrita.Array.open(s, "l4_sample/color/1")
    print(a.metadata)


def test_simple():
    data = np.arange(0, 256, dtype="uint16").reshape((16, 16))
    s = zarrita.FileSystemStore("file://./testdata")
    a = zarrita.Array.create(
        s,
        "simple",
        shape=data.shape,
        chunk_shape=(16, 16),
        dtype=data.dtype,
        fill_value=0,
    )

    a[:, :] = data
    assert np.array_equal(data, a[:, :])


def test_morton():
    assert list(morton_order_iter((2, 2))) == [(0, 0), (1, 0), (0, 1), (1, 1)]
    assert list(morton_order_iter((2, 2, 2))) == [
        (0, 0, 0),
        (1, 0, 0),
        (0, 1, 0),
        (1, 1, 0),
        (0, 0, 1),
        (1, 0, 1),
        (0, 1, 1),
        (1, 1, 1),
    ]
    assert list(morton_order_iter((2, 2, 2, 2))) == [
        (0, 0, 0, 0),
        (1, 0, 0, 0),
        (0, 1, 0, 0),
        (1, 1, 0, 0),
        (0, 0, 1, 0),
        (1, 0, 1, 0),
        (0, 1, 1, 0),
        (1, 1, 1, 0),
        (0, 0, 0, 1),
        (1, 0, 0, 1),
        (0, 1, 0, 1),
        (1, 1, 0, 1),
        (0, 0, 1, 1),
        (1, 0, 1, 1),
        (0, 1, 1, 1),
        (1, 1, 1, 1),
    ]
