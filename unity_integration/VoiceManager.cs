using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using System;

public class VoiceManager : MonoBehaviour
{
    [Header("Voice Settings")]
    public AudioSource audioSource;
    
    [Header("Male Voice Settings")]
    public float maleBasePitch = 0.8f;
    public float maleBaseSpeed = 0.9f;
    
    [Header("Female Voice Settings")]
    public float femaleBasePitch = 1.2f;
    public float femaleBaseSpeed = 1.0f;
    
    private CharacterManager characterManager;
    private Dictionary<string, AudioClip> voiceCache = new Dictionary<string, AudioClip>();
    
    // 事件
    public static event Action<string> OnVoiceStarted;
    public static event Action OnVoiceFinished;
    
    void Start()
    {
        characterManager = FindObjectOfType<CharacterManager>();
        
        if (audioSource == null)
            audioSource = GetComponent<AudioSource>();
    }
    
    public void PlayVoiceForCharacter(string characterId, string text)
    {
        StartCoroutine(PlayVoiceCoroutine(characterId, text));
    }
    
    IEnumerator PlayVoiceCoroutine(string characterId, string text)
    {
        CharacterData character = characterManager.GetCharacterData(characterId);
        if (character == null)
        {
            Debug.LogError($"未找到角色: {characterId}");
            yield break;
        }
        
        // 通知开始语音
        OnVoiceStarted?.Invoke(characterId);
        
        // 通知角色开始说话
        GameObject characterObj = characterManager.loadedCharacters[characterId];
        if (characterObj != null)
        {
            CharacterController3D controller = characterObj.GetComponent<CharacterController3D>();
            if (controller != null)
            {
                controller.StartSpeaking();
            }
        }
        
        // 配置语音参数
        ConfigureVoiceForCharacter(character);
        
        // 获取语音音频
        yield return StartCoroutine(GetVoiceAudio(text, character));
        
        // 播放完成后通知
        yield return new WaitUntil(() => !audioSource.isPlaying);
        
        // 通知角色停止说话
        if (characterObj != null)
        {
            CharacterController3D controller = characterObj.GetComponent<CharacterController3D>();
            if (controller != null)
            {
                controller.StopSpeaking();
            }
        }
        
        OnVoiceFinished?.Invoke();
    }
    
    void ConfigureVoiceForCharacter(CharacterData character)
    {
        VoiceSettings voiceSettings = character.voice_settings;
        
        // 根据性别设置基础参数
        if (character.gender == "male")
        {
            audioSource.pitch = maleBasePitch * voiceSettings.pitch;
        }
        else
        {
            audioSource.pitch = femaleBasePitch * voiceSettings.pitch;
        }
        
        // 可以在这里添加更多语音配置
        audioSource.volume = 1.0f;
    }
    
    IEnumerator GetVoiceAudio(string text, CharacterData character)
    {
        // 检查缓存
        string cacheKey = $"{character.id}_{text.GetHashCode()}";
        if (voiceCache.ContainsKey(cacheKey))
        {
            audioSource.clip = voiceCache[cacheKey];
            audioSource.Play();
            yield break;
        }
        
        // 调用后端TTS服务
        yield return StartCoroutine(RequestTTSFromBackend(text, character, cacheKey));
    }
    
    IEnumerator RequestTTSFromBackend(string text, CharacterData character, string cacheKey)
    {
        // 构建请求数据
        var requestData = new
        {
            text = text,
            character_id = character.id,
            voice_type = character.voice_type,
            voice_settings = character.voice_settings
        };
        
        string jsonData = JsonUtility.ToJson(requestData);
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
        
        // 发送请求到后端
        using (UnityWebRequest request = new UnityWebRequest("http://localhost:5000/api/tts", "POST"))
        {
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerAudioClip("", AudioType.WAV);
            request.SetRequestHeader("Content-Type", "application/json");
            
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                AudioClip clip = DownloadHandlerAudioClip.GetContent(request);
                if (clip != null)
                {
                    // 缓存音频
                    voiceCache[cacheKey] = clip;
                    
                    // 播放音频
                    audioSource.clip = clip;
                    audioSource.Play();
                }
                else
                {
                    Debug.LogError("无法获取音频数据");
                }
            }
            else
            {
                Debug.LogError($"TTS请求失败: {request.error}");
                // 使用备用的本地TTS或静音
                PlayFallbackAudio(text);
            }
        }
    }
    
    void PlayFallbackAudio(string text)
    {
        // 这里可以实现备用的TTS方案
        Debug.Log($"使用备用语音播放: {text}");
        
        // 模拟播放时间
        StartCoroutine(SimulateAudioPlayback(text.Length * 0.1f));
    }
    
    IEnumerator SimulateAudioPlayback(float duration)
    {
        yield return new WaitForSeconds(duration);
    }
    
    public void StopVoice()
    {
        if (audioSource.isPlaying)
        {
            audioSource.Stop();
        }
    }
    
    public bool IsPlaying()
    {
        return audioSource.isPlaying;
    }
    
    public void ClearVoiceCache()
    {
        voiceCache.Clear();
    }
    
    // 预设语音类型
    public void SetVoicePreset(string presetName)
    {
        switch (presetName.ToLower())
        {
            case "wise_male":
                audioSource.pitch = 0.8f;
                break;
            case "young_male":
                audioSource.pitch = 1.1f;
                break;
            case "scientist_male":
                audioSource.pitch = 0.9f;
                break;
            case "poet_male":
                audioSource.pitch = 0.85f;
                break;
            case "sage_male":
                audioSource.pitch = 0.75f;
                break;
            case "scientist_female":
                audioSource.pitch = 1.2f;
                break;
            case "teacher_female":
                audioSource.pitch = 1.1f;
                break;
            default:
                audioSource.pitch = 1.0f;
                break;
        }
    }
}