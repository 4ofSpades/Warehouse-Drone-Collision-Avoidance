using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

public class CollisionHandler : MonoBehaviour
{

    //UI
    public Text scoreText;
    public Text timeText;

    //Self-explanatory vars?
    private bool gameOver = false;
    public bool GameOver { get => gameOver; }
    private float score;
    public float Score { get => score; }
    private int targetsLeft, totalAmountTargets;

    //Time In seconds
    private float timeLeft;

    private void Start()
    {
        this.score = 0;
        this.timeLeft = 0;
        this.scoreText = GameObject.Find("Score Text").GetComponent<Text>();
        this.timeText = GameObject.Find("Time Text").GetComponent<Text>();
        scoreText.text = "Score: " + score.ToString();
        timeText.text = "Time: " + timeLeft.ToString();
        ////TODO, Move scoring to another class
        //totalAmountTargets = gameObject.GetComponentInParent<StageGenerator>().AmountOfTargets;
        //targetsLeft = totalAmountTargets;
    }

    private void Update()
    {
        timeLeft += Time.deltaTime;
        timeText.text = "Time: " + timeLeft.ToString();
        if (timeLeft <= 0.0)
        {
            //Restart();
        }
    }

    public void OnCollisionEnter(Collision other)
    {
        //Debug.Log("OnCollisionEnter invoked: " + other.collider.name);
        //GameObject.Find("Academy").GetComponent<DroneAcademy>().AcademyReset();
    }

    public void OnTriggerEnter(Collider other)
    { 
        //Debug.Log("Triggered by: " + other);
        
        //UpdateScore();
        //targetsLeft--;
        //if (targetsLeft <= 0)
        //{
        //    Restart();
        //}
    }

    public void UpdateScore()
    {
        score += (1.0f / totalAmountTargets) * 100;
        scoreText.text = "Score: " + score.ToString() + "%";
    }
}
