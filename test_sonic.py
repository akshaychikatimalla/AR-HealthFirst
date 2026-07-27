import boto3

polly = boto3.client("polly", region_name="us-east-1")

# Test English - neural engine
response = polly.synthesize_speech(
    Text="Take one tablet after food. Safe with your medicines. Remember to store in a cool dry place.",
    OutputFormat="mp3",
    VoiceId="Joanna",
    LanguageCode="en-US",
    Engine="neural"
)
with open("test_english.mp3", "wb") as f:
    f.write(response["AudioStream"].read())
print("English: SUCCESS")

# Test Hindi - standard engine (Aditi doesn't support neural)
response = polly.synthesize_speech(
    Text="दवाई लें। खाने के बाद एक गोली लें। याद रखें, पानी के साथ लें।",
    OutputFormat="mp3",
    VoiceId="Aditi",
    LanguageCode="hi-IN",
    Engine="standard"
)
with open("test_hindi.mp3", "wb") as f:
    f.write(response["AudioStream"].read())
print("Hindi: SUCCESS")

# Test Telugu - standard engine
response = polly.synthesize_speech(
    Text="మందు సమాచారం. భోజనం తర్వాత ఒక మాత్ర తీసుకోండి.",
    OutputFormat="mp3",
    VoiceId="Kajal",
    LanguageCode="te-IN",
    Engine="neural"
)
with open("test_telugu.mp3", "wb") as f:
    f.write(response["AudioStream"].read())
print("Telugu: SUCCESS")