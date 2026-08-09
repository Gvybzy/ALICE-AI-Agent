try {
    Add-Type -AssemblyName System.Speech
    $recognizer = New-Object System.Speech.Recognition.SpeechRecognitionEngine
    $grammar = New-Object System.Speech.Recognition.DictationGrammar
    $recognizer.LoadGrammar($grammar)
    $recognizer.SetInputToDefaultAudioDevice()

    # Give up after 10 seconds instead of listening forever if nothing is heard.
    $result = $recognizer.Recognize([TimeSpan]::FromSeconds(10))

    if ($result) {
        Write-Output $result.Text
    }
    # If nothing was heard, print nothing - agent.py already handles an empty result.
}
catch {
    # e.g. no microphone available, or the Speech component isn't installed.
    Write-Error "Voice recognition failed: $($_.Exception.Message)"
}
