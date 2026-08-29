import winreg
import pyttsx3


REG_PATH = r"SOFTWARE\Microsoft\Speech_OneCore\Voices\Tokens"


def find_hindi_voice():

    key = winreg.OpenKey(
        winreg.HKEY_LOCAL_MACHINE,
        REG_PATH
    )

    count = winreg.QueryInfoKey(key)[0]

    for i in range(count):

        name = winreg.EnumKey(key, i)

        voice_key = winreg.OpenKey(key, name)

        try:
            voice_name = winreg.QueryValueEx(
                voice_key,
                ""
            )[0]

            if "Hindi" in voice_name:

                print("Found:", voice_name)

                return name

        finally:
            winreg.CloseKey(voice_key)

    winreg.CloseKey(key)

    return None


voice_id = find_hindi_voice()

print("Voice ID:", voice_id)

if voice_id:

    engine = pyttsx3.init()

    # pyttsx3 normally expects the SAPI voice ID,
    # so we will inspect what it can see first.
    print("\nAvailable pyttsx3 voices:")

    for voice in engine.getProperty("voices"):
        print(voice.id)

else:
    print("Hindi voice not found.")