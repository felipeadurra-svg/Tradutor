from types import SimpleNamespace

from app.services.transcription import TranscriptionService


def test_extract_segments_accepts_dict_segments():
    transcript = SimpleNamespace(
        segments=[
            {
                "id": 1,
                "seek": 10,
                "start": 1.5,
                "end": 3.0,
                "text": "hello",
                "tokens": [1, 2],
                "temperature": 0.1,
                "avg_logprob": -0.2,
                "compression_ratio": 1.1,
                "no_speech_prob": 0.05,
            }
        ]
    )

    result = TranscriptionService._extract_segments(transcript)

    assert result == [
        {
            "id": 1,
            "seek": 10,
            "start": 1.5,
            "end": 3.0,
            "text": "hello",
            "tokens": [1, 2],
            "temperature": 0.1,
            "avg_logprob": -0.2,
            "compression_ratio": 1.1,
            "no_speech_prob": 0.05,
        }
    ]


def test_extract_segments_accepts_attribute_segments():
    transcript = SimpleNamespace(
        segments=[
            SimpleNamespace(
                id=2,
                seek=20,
                start=4.0,
                end=6.5,
                text="world",
                tokens=[3, 4],
                temperature=0.2,
                avg_logprob=-0.3,
                compression_ratio=1.2,
                no_speech_prob=0.01,
            )
        ]
    )

    result = TranscriptionService._extract_segments(transcript)

    assert result == [
        {
            "id": 2,
            "seek": 20,
            "start": 4.0,
            "end": 6.5,
            "text": "world",
            "tokens": [3, 4],
            "temperature": 0.2,
            "avg_logprob": -0.3,
            "compression_ratio": 1.2,
            "no_speech_prob": 0.01,
        }
    ]
