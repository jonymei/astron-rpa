from unittest.mock import patch, mock_open
from astronverse.openapi.ocr import train_ticket, taxi_ticket


@patch("astronverse.openapi.ocr._common.GatewayClient.post_multipart")
def test_train_ticket_alias(mock_post):
    mock_post.return_value = {"payload": {"ticket_no": "G1234"}}
    with patch("astronverse.openapi.ocr._common.utils.generate_src_files", return_value=["/fake/train.jpg"]):
        with patch("builtins.open", mock_open(read_data=b"fake_bytes")):
            result = train_ticket(src_file="/fake/train.jpg", is_save=False)
    assert len(result) == 1
    call_args = mock_post.call_args
    assert call_args.args[3]["ocr_type"] == "train_ticket"


@patch("astronverse.openapi.ocr._common.GatewayClient.post_multipart")
def test_taxi_ticket_alias(mock_post):
    mock_post.return_value = {"payload": {"ticket_no": "T5678"}}
    with patch("astronverse.openapi.ocr._common.utils.generate_src_files", return_value=["/fake/taxi.jpg"]):
        with patch("builtins.open", mock_open(read_data=b"fake_bytes")):
            result = taxi_ticket(src_file="/fake/taxi.jpg", is_save=False)
    assert len(result) == 1
    call_args = mock_post.call_args
    assert call_args.args[3]["ocr_type"] == "taxi_receipt"
