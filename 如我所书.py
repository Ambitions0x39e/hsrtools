from format import Formatter, Syntax
import json, pathlib, subprocess, contextlib, sys
from io import StringIO
# Defines format
_formatter = Formatter(syntax=Syntax.MediaWikiPretty)
'''
TarotBookEnergy: 单次提交显示的对应剧情内容
TarotBookCharacter: 每个角色对应的剧情
TarotBookSentence: 剧情细节
'''
''' Only requires 'TextMapCHS', 'TarotBook' related files '''
'''
在3.0版本中，缇宝-如我所书-第二章节种出现了顺序和TextMap，ExcelOutput不对应的部分。
其他的内容，检查后目前为止并没有类似的问题，所以按照ExcelOutput的顺序输出。
'''
TextMapCHS, TextMapKR, TextMapEN, TextMapJP = None, None, None, None 
TB_Energy, TB_Character, TB_Sentence, TB_Config, TB_Clue = None, None, None, None, None
GameDataPath = pathlib.Path("~/Downloads/turnbasedgamedata/").expanduser()

def load_TextMap() -> None:
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

def load_TarotBookDetails() -> None:
    global TB_Energy, TB_Character, TB_Sentence, TB_Config, TB_Clue
    TB_Energy = json.load(open(
        GameDataPath.joinpath("ExcelOutput", "TarotBookEnergy.json"), 
        "r", 
        encoding = "utf-8"))  
    
    TB_Character = json.load(open(
        GameDataPath.joinpath("ExcelOutput", "TarotBookCharacter.json"), 
        "r", 
        encoding = "utf-8"))
    
    TB_Sentence= json.load(open(
        GameDataPath.joinpath("ExcelOutput", "TarotBookSentence.json"), 
        "r", 
        encoding = "utf-8"))

    TB_Config = json.load(open(
        GameDataPath.joinpath("Config", "ConfigBooklet", "TarotBook", "TarotBookConfig.json"),
        "r",
        encoding = "utf-8"
    ))["ChapterConfigList"]
    
    TB_Clue = json.load(open(
        GameDataPath.joinpath("ExcelOutput", "TarotBookClue.json"),
        "r",
        encoding = "utf-8"
    ))

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

class TarotBookDataModel:
    def __init__(self, **kwargs):
        ''' Set attributes. '''
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __str__(self):
        return f"TarotBookDataModel({self.__dict__})"

    def __repr__(self):
        return self.__str__()
    
def load_from_json(file_path) -> list[TarotBookDataModel] | TarotBookDataModel | None:
    try:
        with open(file_path, "r", encoding='utf-8') as file:
            data = json.load(file)

        if isinstance(data, list):
            return [TarotBookDataModel(**item) for item in data]
        else:
            return TarotBookDataModel(**data)
    
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Json file {file_path} has incorrect format.")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None
    
def load_TB_Energy() -> None:
    global GameDataPath
    print("==== 可能显示的提交提示 ====")
    for data in TB_Energy:
        try:
            print(f"* {_formatter.format(TextMapCHS[str((data['Toast'])['Hash'])])}", sep='')
        except KeyError:
            pass

def load_TB_MainContent() -> None:
    for data in TB_Character:
        print(f"=== {_formatter.format(TextMapCHS[str((data['Name'])['Hash'])])} ===")
        for storyList in data["StoryList"]:
            print(f"==== ID: {str(storyList)} ====")
            last = None
            for sentences in TB_Sentence:
                if str(sentences["ID"]).startswith(str(storyList)):
                    if last == None or (last != sentences["ID"]//100 and last != None):
                        print("===== ID: " + str(sentences["ID"]//100) + " =====")
                        last = sentences["ID"]//100
                    print(
                        _formatter.format(
                            TextMapCHS[str((sentences["Sentence"])["Hash"])]
                        )
                    )

def load_TB_Sub_Chapter_Title() -> None:
    for data in TB_Config:
        print("{{面包屑|如我所书}}")
        try:
            print("= " + 
                _formatter.format(
                    TextMapCHS[str(data["Title"]["Hash"])]
                ) + " ="
            )
        except KeyError:
            pass
        for sect in data["SectionSynopsisList"]:
            try:
                if _formatter.format(TextMapCHS[str(sect["Title"]["Hash"])]) == _formatter.format(TextMapCHS[str(data["Title"]["Hash"])]):
                    continue
                print( "== "+
                    _formatter.format(
                        TextMapCHS[str(sect["Title"]["Hash"])]
                    ) + " =="
                )
            except KeyError as e:
                pass
            
    
def load_TB_Clue() -> None:
    for data in TB_Character:
        print(f"=== {_formatter.format(TextMapCHS[str((data['Name'])['Hash'])])} ===")
        for storyList in data["StoryList"]:
            print(f"==== ID: {str(storyList)} ====")
            print('<table style="width: 100%; text-align: center">')
            print('<tr>')
            for clues in TB_Clue:
                if str(clues["ID"]).startswith(str(storyList)):
                    print(
                        '<td style="width:33.33%" > '+
                        _formatter.format(
                            TextMapCHS[str((clues["Name"])["Hash"])]
                        ) 
                        + ' </td>'
                    )
            print('</tr>\n</table>')

if __name__ == "__main__":
    load_TextMap()
    load_TarotBookDetails()
    
    with open("Energy.txt", "w", encoding="utf-8") as f:
        with contextlib.redirect_stdout(f):
            load_TB_Energy()
    
    with open("MainContent.txt", "w", encoding="utf-8") as f:
        with contextlib.redirect_stdout(f):
            load_TB_MainContent()
    
    for data in TB_Character: 
        print(
           '如我所书-'+_formatter.format(TextMapCHS[str(data["MainCatalogTitle"]["Hash"])]), sep="."
        )
    
    with open("SubChapterTitle.txt", "w", encoding="utf-8") as f:
        with contextlib.redirect_stdout(f):
            load_TB_Sub_Chapter_Title()
            
    with open("Clues.txt", "w", encoding="utf-8") as f:
        with contextlib.redirect_stdout(f):
            load_TB_Clue()
            
    arr = [1] * 2000
    while True:
        tmp = int(input())
        part1, part2 = None, None
        title_comp = None
        part1ID, part2ID = None, None
        for data in TB_Character:
            if tmp in data["StoryList"]:
                part1 = "如我所书-" + TextMapCHS[str(data["MainCatalogTitle"]["Hash"])]
                title_comp = TextMapCHS[str(object=data["Name"]["Hash"])]
                break
        
        # print(title_comp)
        collector = OutputCollector()
        sys.stdout = collector
        for data in TB_Config:
            try:
                # print('-'+TextMapCHS[str(data["Title"]["Hash"])])
                if TextMapCHS[str(data["Title"]["Hash"])] == title_comp:
                    for sects in data["SectionSynopsisList"]:
                        if str(sects["ID"]).startswith(str(tmp)):
                            part2 = _formatter.format(TextMapCHS[str(sects["Title"]["Hash"])])
                            break
            except KeyError:
                pass
        
        if arr[tmp] == None:
            arr[tmp]=0
        
        print(part1+'-'+part2+'-'+str(arr[tmp]), sep="", end="")
        arr[tmp]+=1
        if collector.copy_to_clipboard():
            print("\n内容已复制到剪贴板。")
        else:
            print("\n内容复制失败。")