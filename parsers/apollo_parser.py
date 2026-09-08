from cyber_record.record import Record
from record_msg.parser import to_csv, ImageParser, PointCloudParser
from google.protobuf.json_format import MessageToDict
import csv
from operator import attrgetter

from data_exchange import exchange

def get_all_channels():
    '''解析所有 channel 的列表'''
    record = Record(exchange.packet_path)
    exchange.channels = [ch.name for ch in record.get_channel_cache()]
    return True

def get_messages():
    '''解析所选择 channel 中的所有messages (第一帧)'''
    record = Record(exchange.packet_path)
    messages = record.read_messages(exchange.selected_channel)
    try:
        topic, message, timestamp = next(messages)
        message_dict = MessageToDict(
            message,
            preserving_proto_field_name=True
        )
        exchange.messages = message_dict
    except StopIteration:
        exchange.messages = {}
    return True

def export_csv():
    '''将exchange.selected_messages中的chaneel的数据导出为csv文件'''
    record = Record(exchange.packet_path)
    output_path = f'{exchange.output_dir}/output.csv'
    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        # 写入表头
        writer.writerow(exchange.selected_messages)
        for topic, message, timestamp in record.read_messages(exchange.selected_channel):
            values = [
                attrgetter(selected_message)(message)
                for selected_message in exchange.selected_messages
            ]
            line = to_csv(values) 
            writer.writerow(line)
    return True  

def export_jpg():
    '''将exchange.selected_channel中的图片数据导出为jpg文件'''
    record = Record(exchange.packet_path)
    image_parser = ImageParser(output_path=exchange.output_dir)
    processed = False  # 标记是否处理过至少一条消息
    for topic, message, t in record.read_messages(exchange.selected_channel):
        image_parser.parse(message, t)
        processed = True
    if processed:
        return True
    else:
        return False

def export_pcd():
    '''将exchange.selected_channel中的点云数据导出为pcd文件'''
    record = Record(exchange.packet_path)
    pointcloud_parser = PointCloudParser(output_path=exchange.output_dir)
    processed = False  # 标记是否处理过至少一条消息
    for topic, message, t in record.read_messages(exchange.selected_channel):
        pointcloud_parser.parse(message, t)
        processed = True
    if processed:
        return True
    else:
        return False           
