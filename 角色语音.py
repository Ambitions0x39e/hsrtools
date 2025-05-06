import json, sys, subprocess, pathlib, fire
import format # Local module, from github.com/xr1s/gsz/gsz/format.py
from io import StringIO
TextMapCHS, TextMapKR, TextMapEN, TextMapJP = None, None, None, None 
GameDataPath = pathlib.Path("~/Downloads/turnbasedgamedata/").expanduser()

def load_TextMap():
    global TextMapCHS, TextMapKR, TextMapEN, TextMapJP

    TextMapCHS=json.load(open(
        GameDataPath.joinpath("TextMap", "TextMapCHS.json"), 
        "r", 
        encoding="utf-8"))
    TextMapKR=json.load(open(
        GameDataPath.joinpath("TextMap", "TextMapKR.json"),
        "r", 
        encoding="utf-8"))
    TextMapEN=json.load(open(
        GameDataPath.joinpath("TextMap", "TextMapEN.json"),
        "r", 
        encoding="utf-8"))
    TextMapJP=json.load(open(
        GameDataPath.joinpath("TextMap", "TextMapJP.json"),
        "r", 
        encoding="utf-8"))

class OutputCollector:
    def __init__(self):
        self.output = StringIO()
        self.original_stdout = sys.stdout
        self.collected_output = []
    
    def write(self, text):
        self.original_stdout.write(text)
        self.collected_output.append(text)
    
    def flush(self):
        self.original_stdout.flush()
    
    def get_output(self):
        return ''.join(self.collected_output)

    def copy_to_clipboard(self):
        try:
            process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
            process.communicate(self.get_output().encode("utf-8"))
            return True
        except Exception as e:
            print(f"Error: {str(e)}")
            return False

class AvatarVoiceDataModel:
    def __init__(self, **kwargs):
        # Dynamically set attributes based on JSON keys
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __str__(self):
        """返回格式化的字符串表示"""
        return f"AvatarVoiceDataModel({self.__dict__})"
    
    def __repr__(self):
        """返回对象的表示形式"""
        return self.__str__()

def load_from_json(file_path):
    try:
        # Read JSON file
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        # If the JSON contains a list of objects
        if isinstance(data, list):
            return [AvatarVoiceDataModel(**item) for item in data]
        # If the JSON contains a single object
        else:
            return AvatarVoiceDataModel(**data)
            
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{file_path}'")
        return None
    except Exception as e:
        print(f"Error: An unexpected error occurred: {str(e)}")
        return None

def generate_voice(name: str):
    global GameDataPath
    load_TextMap()
    VoiceAtlasJson = load_from_json(
        GameDataPath.joinpath("ExcelOutput", "VoiceAtlas.json")
    )
    AvatarConfigJson = load_from_json(
        GameDataPath.joinpath("ExcelOutput", "AvatarConfig.json")
    )
    # name = input("角色名称：")
    target = None
    for i, item in enumerate(AvatarConfigJson, 1):
        if TextMapCHS[str(item.AvatarName["Hash"])]==name:
            target = item.AvatarID
            break
    
    # Redirect all output to clipboard
    collector = OutputCollector()
    sys.stdout = collector
    
    print("{{角色语音表头|", name, "|未完善=是}}", sep="")
    print("{{切换板|开始}}")
    print("{{切换板|默认显示|互动语音}}")
    print("{{切换板|默认折叠|战斗语音}}")
    print("{{切换板|显示内容}}")
    OnceFlag=False
    formats = format.Formatter(syntax=format.Syntax.Plain, game="SRGameData")
    for i, item in enumerate(VoiceAtlasJson, 1):
        if item.AvatarID != target:
            continue
        if hasattr(item, 'IsBattleVoice') and OnceFlag == False:
            print("{{切换板|内容结束}}\n{{切换板|折叠内容}}")
            OnceFlag=True
            
        VoiceTitle = str(item.VoiceTitle['Hash'])
        VoiceM=str(item.Voice_M['Hash'])
        print("{{角色语音")
        print("|语音类型=", formats.format(TextMapCHS[VoiceTitle]), sep="")
        print("|语音文件=", name, "-", formats.format(TextMapCHS[VoiceTitle]), sep="")
        print("|语音内容=", formats.format(TextMapCHS[VoiceM]), sep="")
        print("|语音内容日语=", formats.format(TextMapJP[VoiceM]), sep="")
        print("|语音内容英语=", formats.format(TextMapEN[VoiceM]), sep="")
        print("|语音内容韩语=", formats.format(TextMapKR[VoiceM]), sep="")
        print("}}")
        
        
    print("{{切换板|内容结束}}\n{{切换板|结束}}")
    
    # Copy
    # sys.stdout = collector.original_stdout
    if collector.copy_to_clipboard():
        print("内容已复制到剪贴板。")
    else:
        print("内容复制失败。")
        
if __name__ == "__main__":
    fire.Fire(generate_voice)