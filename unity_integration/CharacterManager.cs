using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;
using Newtonsoft.Json;

[System.Serializable]
public class CharacterData
{
    public string id;
    public string name;
    public string gender;
    public string voice_type;
    public string model_path;
    public string avatar_texture;
    public string animation_controller;
    public VoiceSettings voice_settings;
}

[System.Serializable]
public class VoiceSettings
{
    public float pitch = 1.0f;
    public float speed = 1.0f;
    public string voice_id;
}

[System.Serializable]
public class CharacterConfig
{
    public List<CharacterData> characters;
    public UnitySettings unity_settings;
}

[System.Serializable]
public class UnitySettings
{
    public float character_scale = 1.0f;
    public float animation_blend_time = 0.2f;
    public float voice_fade_time = 0.5f;
    public string model_quality = "high";
}

public class CharacterManager : MonoBehaviour
{
    [Header("Character Configuration")]
    public TextAsset characterConfigFile;
    
    [Header("Character Display")]
    public Transform characterSpawnPoint;
    public Camera characterCamera;
    
    [Header("Audio")]
    public AudioSource voiceAudioSource;
    
    private CharacterConfig config;
    private Dictionary<string, GameObject> loadedCharacters = new Dictionary<string, GameObject>();
    private GameObject currentCharacter;
    private CharacterData currentCharacterData;
    
    // 事件
    public static event Action<string> OnCharacterChanged;
    public static event Action<bool> OnCharacterLoading;
    
    void Start()
    {
        LoadCharacterConfig();
        InitializeCharacterSystem();
    }
    
    void LoadCharacterConfig()
    {
        try
        {
            if (characterConfigFile != null)
            {
                string jsonText = characterConfigFile.text;
                config = JsonConvert.DeserializeObject<CharacterConfig>(jsonText);
                Debug.Log($"成功加载 {config.characters.Count} 个角色配置");
            }
            else
            {
                Debug.LogError("角色配置文件未设置！");
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"加载角色配置失败: {e.Message}");
        }
    }
    
    void InitializeCharacterSystem()
    {
        // 预加载所有角色模型
        StartCoroutine(PreloadCharacters());
    }
    
    IEnumerator PreloadCharacters()
    {
        OnCharacterLoading?.Invoke(true);
        
        foreach (var character in config.characters)
        {
            yield return StartCoroutine(LoadCharacterModel(character));
        }
        
        OnCharacterLoading?.Invoke(false);
        Debug.Log("所有角色模型预加载完成");
    }
    
    IEnumerator LoadCharacterModel(CharacterData characterData)
    {
        if (loadedCharacters.ContainsKey(characterData.id))
            yield break;
            
        // 加载角色模型
        ResourceRequest request = Resources.LoadAsync<GameObject>(characterData.model_path);
        yield return request;
        
        if (request.asset != null)
        {
            GameObject characterPrefab = request.asset as GameObject;
            GameObject characterInstance = Instantiate(characterPrefab, characterSpawnPoint);
            
            // 设置角色缩放
            characterInstance.transform.localScale = Vector3.one * config.unity_settings.character_scale;
            
            // 初始时隐藏
            characterInstance.SetActive(false);
            
            // 设置动画控制器
            Animator animator = characterInstance.GetComponent<Animator>();
            if (animator != null)
            {
                RuntimeAnimatorController controller = Resources.Load<RuntimeAnimatorController>(characterData.animation_controller);
                if (controller != null)
                {
                    animator.runtimeAnimatorController = controller;
                }
            }
            
            // 添加角色组件
            CharacterController3D controller3D = characterInstance.GetComponent<CharacterController3D>();
            if (controller3D == null)
            {
                controller3D = characterInstance.AddComponent<CharacterController3D>();
            }
            controller3D.Initialize(characterData);
            
            loadedCharacters[characterData.id] = characterInstance;
            Debug.Log($"成功加载角色: {characterData.name}");
        }
        else
        {
            Debug.LogError($"无法加载角色模型: {characterData.model_path}");
        }
    }
    
    public void SwitchToCharacter(string characterId)
    {
        CharacterData characterData = GetCharacterData(characterId);
        if (characterData == null)
        {
            Debug.LogError($"未找到角色: {characterId}");
            return;
        }
        
        StartCoroutine(SwitchCharacterCoroutine(characterData));
    }
    
    IEnumerator SwitchCharacterCoroutine(CharacterData characterData)
    {
        OnCharacterLoading?.Invoke(true);
        
        // 隐藏当前角色
        if (currentCharacter != null)
        {
            yield return StartCoroutine(FadeOutCharacter(currentCharacter));
            currentCharacter.SetActive(false);
        }
        
        // 显示新角色
        if (loadedCharacters.ContainsKey(characterData.id))
        {
            currentCharacter = loadedCharacters[characterData.id];
            currentCharacterData = characterData;
            
            currentCharacter.SetActive(true);
            yield return StartCoroutine(FadeInCharacter(currentCharacter));
            
            // 配置语音设置
            ConfigureVoiceSettings(characterData.voice_settings);
            
            OnCharacterChanged?.Invoke(characterData.id);
            Debug.Log($"切换到角色: {characterData.name}");
        }
        
        OnCharacterLoading?.Invoke(false);
    }
    
    IEnumerator FadeOutCharacter(GameObject character)
    {
        Renderer[] renderers = character.GetComponentsInChildren<Renderer>();
        float fadeTime = config.unity_settings.voice_fade_time;
        float elapsedTime = 0;
        
        while (elapsedTime < fadeTime)
        {
            float alpha = Mathf.Lerp(1f, 0f, elapsedTime / fadeTime);
            SetCharacterAlpha(renderers, alpha);
            elapsedTime += Time.deltaTime;
            yield return null;
        }
        
        SetCharacterAlpha(renderers, 0f);
    }
    
    IEnumerator FadeInCharacter(GameObject character)
    {
        Renderer[] renderers = character.GetComponentsInChildren<Renderer>();
        float fadeTime = config.unity_settings.voice_fade_time;
        float elapsedTime = 0;
        
        SetCharacterAlpha(renderers, 0f);
        
        while (elapsedTime < fadeTime)
        {
            float alpha = Mathf.Lerp(0f, 1f, elapsedTime / fadeTime);
            SetCharacterAlpha(renderers, alpha);
            elapsedTime += Time.deltaTime;
            yield return null;
        }
        
        SetCharacterAlpha(renderers, 1f);
    }
    
    void SetCharacterAlpha(Renderer[] renderers, float alpha)
    {
        foreach (Renderer renderer in renderers)
        {
            foreach (Material material in renderer.materials)
            {
                if (material.HasProperty("_Color"))
                {
                    Color color = material.color;
                    color.a = alpha;
                    material.color = color;
                }
            }
        }
    }
    
    void ConfigureVoiceSettings(VoiceSettings voiceSettings)
    {
        if (voiceAudioSource != null)
        {
            voiceAudioSource.pitch = voiceSettings.pitch;
            // 这里可以添加更多语音配置
        }
    }
    
    public void PlayCharacterAnimation(string animationName)
    {
        if (currentCharacter != null)
        {
            Animator animator = currentCharacter.GetComponent<Animator>();
            if (animator != null)
            {
                animator.SetTrigger(animationName);
            }
        }
    }
    
    public void PlayVoiceClip(AudioClip clip)
    {
        if (voiceAudioSource != null && clip != null)
        {
            voiceAudioSource.clip = clip;
            voiceAudioSource.Play();
        }
    }
    
    public CharacterData GetCharacterData(string characterId)
    {
        return config.characters.Find(c => c.id == characterId);
    }
    
    public List<CharacterData> GetAllCharacters()
    {
        return config.characters;
    }
    
    public CharacterData GetCurrentCharacter()
    {
        return currentCharacterData;
    }
    
    public bool IsCharacterMale(string characterId)
    {
        CharacterData character = GetCharacterData(characterId);
        return character != null && character.gender == "male";
    }
    
    public string GetVoiceType(string characterId)
    {
        CharacterData character = GetCharacterData(characterId);
        return character?.voice_type ?? "male";
    }
}