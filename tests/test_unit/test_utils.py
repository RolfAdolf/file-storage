from unittest import TestCase

from pathlib import Path

from src.utils import hashes, filenames


test_media_samples = Path("./samples/")

test_files = (
    ("file_example_JPEG_4MB.jpeg", "image/jpeg"),
    ("file_example_MP3_5MG.mp3", "audio/mpeg"),
    ("file_example_PDF_15MB.pdf", "application/pdf"),
    ("file_example_PNG_3MB.png", "image/png"),
    ("file_example_WAV_10MG.wav", "audio/x-wav"),
)


class HashesTests(TestCase):
    def test_generate_string(self):
        self.assertNotEqual(
            hashes.generate_random_string(),
            hashes.generate_random_string(),
        )

    def test_hashes_gen(self):
        for test_file in test_files:
            with open(test_media_samples / test_file[0], "rb") as f:
                try:
                    hashes.file_hash("username", f.read())
                except Exception as e:
                    self.assertFalse(True, e)


class FilenamesTests(TestCase):
    def test_collect_name(self):
        old_filename = "test_text.txt"
        new_stem = hashes.generate_random_string()
        self.assertEqual(
            new_stem + ".txt",
            str(filenames.collect_new_name(new_stem, old_filename)),
        )
