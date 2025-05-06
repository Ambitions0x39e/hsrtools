import json, sys, pathlib, fire
from regex import P
import format # local format from xr1s/gsz
TextMapCHS = None
GameDataPath = pathlib.Path("~/Downloads/turnbasedgamedata/").expanduser()
formats = format.Formatter(syntax=format.Syntax.Terminal, game="SRGameData")
def load_textmap():
    global TextMapCHS
    TextMapCHS=json.load(open(
        GameDataPath.joinpath("TextMap", "TextMapCHS.json"), 
        "r", 
        encoding="utf-8"))
    
class AvatarMail:
    def __init__(self, **kwargs):
        # Dynamically set attributes based on JSON keys
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __str__(self):
        """返回格式化的字符串表示"""
        return f"AvatarMail({self.__dict__})"
    
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
            return [AvatarMail(**item) for item in data]
        # If the JSON contains a single object
        else:
            return AvatarMail(**data)
            
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{file_path}'")
        return None
    except Exception as e:
        print(f"Error: An unexpected error occurred: {str(e)}")
        return None
    

def main():
    global GameDataPath, TextMapCHS, formats
    ActivityAvatarDeliverConfig = load_from_json(
        GameDataPath.joinpath("ExcelOutput", "ActivityAvatarDeliverConfig.json")
    )
    AvatarConfig = load_from_json(
        GameDataPath.joinpath("ExcelOutput", "AvatarConfig.json")
    )
    for i, item in enumerate(ActivityAvatarDeliverConfig, 1):
        ChName = None
        for j, items in enumerate(AvatarConfig, 1):
            if items.AvatarID == item.AvatarID:
                ChName = str(items.AvatarName["Hash"])
        Name = str(item.Name['Hash'])
        MailDesc = str(item.MailDesc['Hash'])
        Sign = str(item.Sign['Hash'])
        print(formats.format(TextMapCHS[ChName]))
        print(formats.format(TextMapCHS[Name]))
        print(formats.format(TextMapCHS[MailDesc]))
        print(formats.format(TextMapCHS[Sign]))
        print("====")
        
        
if __name__ == "__main__":
    load_textmap()
    main()