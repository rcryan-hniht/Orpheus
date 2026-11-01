import os
from unittest.mock import MagicMock

from orpheus.cava import CavaReader
from orpheus.phases.now_playing import CavaVisualizer


def test_cava_reader_init():
    reader = CavaReader(num_bars=32, framerate=30)
    assert reader.num_bars == 32
    assert reader.framerate == 30
    assert len(reader.get_bars()) == 32
    assert all(b == 0.0 for b in reader.get_bars())


def test_cava_reader_set_bars():
    reader = CavaReader(num_bars=8)
    reader.set_bars([0.1, 0.2, 0.5, 0.9])
    bars = reader.get_bars()
    assert bars[:4] == [0.1, 0.2, 0.5, 0.9]
    assert bars[4:] == [0.0, 0.0, 0.0, 0.0]


def test_cava_reader_binary_read_loop():
    reader = CavaReader(num_bars=4)
    # Simulate binary frame of 4 bytes: 0, 64, 128, 255
    raw_bytes = bytes([0, 64, 128, 255])

    fake_proc = MagicMock()
    fake_proc.stdout.read.side_effect = [raw_bytes, b""]
    fake_proc.poll.return_value = None

    reader._proc = fake_proc
    reader._running = True
    reader._read_loop()

    bars = reader.get_bars()
    assert len(bars) == 4
    assert bars[0] == 0.0
    assert abs(bars[1] - (64 / 255.0)) < 1e-4
    assert abs(bars[2] - (128 / 255.0)) < 1e-4
    assert abs(bars[3] - 1.0) < 1e-4


def test_cava_reader_start_and_stop_cleanup(tmp_path):
    reader = CavaReader(num_bars=16)
    conf_file = str(tmp_path / "cava.conf")
    with open(conf_file, "w") as f:
        f.write("mock")
    reader._conf_path = conf_file

    fake_proc = MagicMock()
    reader._proc = fake_proc
    reader._running = True

    reader.stop()
    assert reader._running is False
    assert reader._proc is None
    fake_proc.terminate.assert_called_once()
    assert not os.path.exists(conf_file)


def test_cava_visualizer_reads_cava_reader():
    cava = CavaVisualizer(num_bars=16)
    cava._cava_reader = CavaReader(num_bars=16)
    # Inject real audio spectrum values into reader
    test_bars = [0.25, 0.5, 0.75, 1.0] + [0.1] * 12
    cava._cava_reader.set_bars(test_bars)

    cava.set_playback(is_playing=True, is_paused=False)
    cava._tick()

    # Check heights are scaled by display_height H (1.0 default for unmounted)
    assert cava._heights[0] == 0.25
    assert cava._heights[1] == 0.5
    assert cava._heights[2] == 0.75
    assert cava._heights[3] == 1.0

    # Multi-row scaling: H = 10
    cava._custom_height = 10
    cava._tick()
    assert cava._heights[0] == 2.5
    assert cava._heights[1] == 5.0
    assert cava._heights[2] == 7.5
    assert cava._heights[3] == 10.0
