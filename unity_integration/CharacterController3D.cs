using System.Collections;
using UnityEngine;

public class CharacterController3D : MonoBehaviour
{
    [Header("Character Info")]
    public CharacterData characterData;
    
    [Header("Animation")]
    public Animator animator;
    
    [Header("Voice Visualization")]
    public Transform mouthTransform;
    public float mouthMovementScale = 0.1f;
    
    [Header("Idle Animations")]
    public float idleAnimationInterval = 5f;
    public string[] idleAnimations = { "Idle_Blink", "Idle_LookAround", "Idle_Stretch" };
    
    private bool isSpeaking = false;
    private Coroutine idleCoroutine;
    private Vector3 originalMouthScale;
    
    void Start()
    {
        if (animator == null)
            animator = GetComponent<Animator>();
            
        if (mouthTransform != null)
            originalMouthScale = mouthTransform.localScale;
            
        StartIdleAnimations();
    }
    
    public void Initialize(CharacterData data)
    {
        characterData = data;
        
        // 根据性别设置不同的动画参数
        if (animator != null)
        {
            animator.SetBool("IsMale", data.gender == "male");
            animator.SetFloat("VoicePitch", data.voice_settings.pitch);
        }
    }
    
    void StartIdleAnimations()
    {
        if (idleCoroutine != null)
            StopCoroutine(idleCoroutine);
            
        idleCoroutine = StartCoroutine(IdleAnimationLoop());
    }
    
    IEnumerator IdleAnimationLoop()
    {
        while (true)
        {
            yield return new WaitForSeconds(idleAnimationInterval);
            
            if (!isSpeaking && idleAnimations.Length > 0)
            {
                string randomIdle = idleAnimations[Random.Range(0, idleAnimations.Length)];
                PlayAnimation(randomIdle);
            }
        }
    }
    
    public void StartSpeaking()
    {
        isSpeaking = true;
        
        if (animator != null)
        {
            animator.SetBool("IsSpeaking", true);
            
            // 根据性别播放不同的说话动画
            if (characterData.gender == "male")
            {
                animator.SetTrigger("MaleSpeaking");
            }
            else
            {
                animator.SetTrigger("FemaleSpeaking");
            }
        }
        
        StartCoroutine(MouthMovementCoroutine());
    }
    
    public void StopSpeaking()
    {
        isSpeaking = false;
        
        if (animator != null)
        {
            animator.SetBool("IsSpeaking", false);
        }
        
        if (mouthTransform != null)
        {
            mouthTransform.localScale = originalMouthScale;
        }
    }
    
    IEnumerator MouthMovementCoroutine()
    {
        while (isSpeaking)
        {
            if (mouthTransform != null)
            {
                float movement = Random.Range(0.5f, 1.5f) * mouthMovementScale;
                Vector3 newScale = originalMouthScale + Vector3.one * movement;
                mouthTransform.localScale = newScale;
            }
            
            yield return new WaitForSeconds(Random.Range(0.1f, 0.3f));
        }
    }
    
    public void PlayAnimation(string animationName)
    {
        if (animator != null)
        {
            animator.SetTrigger(animationName);
        }
    }
    
    public void PlayEmotionAnimation(string emotion)
    {
        if (animator != null)
        {
            // 根据性别和情感播放不同动画
            string animationName = $"{characterData.gender}_{emotion}";
            animator.SetTrigger(animationName);
        }
    }
    
    public void LookAtCamera()
    {
        Camera mainCamera = Camera.main;
        if (mainCamera != null)
        {
            Vector3 direction = mainCamera.transform.position - transform.position;
            direction.y = 0; // 只在水平面旋转
            
            if (direction != Vector3.zero)
            {
                Quaternion targetRotation = Quaternion.LookRotation(direction);
                StartCoroutine(SmoothRotate(targetRotation));
            }
        }
    }
    
    IEnumerator SmoothRotate(Quaternion targetRotation)
    {
        Quaternion startRotation = transform.rotation;
        float elapsedTime = 0;
        float rotationTime = 1f;
        
        while (elapsedTime < rotationTime)
        {
            transform.rotation = Quaternion.Slerp(startRotation, targetRotation, elapsedTime / rotationTime);
            elapsedTime += Time.deltaTime;
            yield return null;
        }
        
        transform.rotation = targetRotation;
    }
    
    void OnDestroy()
    {
        if (idleCoroutine != null)
        {
            StopCoroutine(idleCoroutine);
        }
    }
}