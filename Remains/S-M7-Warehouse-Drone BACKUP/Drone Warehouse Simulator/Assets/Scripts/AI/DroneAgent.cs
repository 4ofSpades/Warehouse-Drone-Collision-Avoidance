using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using MLAgents;
using System;
using static DroneMovementScript;
using UnityEngine.UI;

public class DroneAgent : Agent
{
    //Stage generation
    StageGenerator stageGenerator;

    //Rigidbody
    PositioningForces altitudeForces, velocityForces, strafeForces, yawForces;
    public float frontal, side, altitude, rotation;
    Rigidbody drone;

    //Visual
    int score;
    Text scoreText;

    //VectorObs
    Vector3 targetPos;
    public bool useVectorObs;
    RayPerception rayPer;

    public override void InitializeAgent()
    {
        base.InitializeAgent();

        //Stage generation
        this.stageGenerator = GetComponentInParent<StageGenerator>();

        //Rigidbody
        this.altitudeForces = new PositioningForces(-4, 4, 0, -8, 8, 8);
        this.velocityForces = new PositioningForces(-10, 10, 0, -5, 5, 10);
        this.strafeForces = new PositioningForces(-5, 5, 0, -10, 10, 10);
        this.yawForces = new PositioningForces(-360, 360, 0, -90, 90, 180);
        this.drone = GetComponent<Rigidbody>();

        //VectorObs
        this.targetPos = stageGenerator.TargetLocation;
        this.rayPer = GetComponent<RayPerception>();

        //Scoring
        this.score = 0;
        this.scoreText= GameObject.Find("ScoreText" + tag).GetComponent<Text>();
    }

    /// <summary>
    /// Invokes when the agent is marked done
    /// </summary>
    public override void AgentReset()
    {
        stageGenerator.RespawnPlayer();
    }

    /// <summary>
    /// Stops the drone instantly and respawns it with 0 rotation. Finally also marks the drone done and sets the reward to -10 for colliding.
    /// </summary>
    /// <param name="other"></param>
    public void OnCollisionEnter(Collision other)
    {
        Debug.Log("OnCollisionEnter invoked: " + other.collider.name);
        velocityForces.CurrentForce = 0;
        altitudeForces.CurrentForce = 0;
        strafeForces.CurrentForce = 0;
        yawForces.CurrentForce = 0;

        drone.rotation = Quaternion.Euler(Vector3.zero);
        drone.angularVelocity = Vector3.zero;
        drone.velocity = Vector3.zero;
        
        Done();
        SetReward(-10f);
    }

    /// <summary>
    /// Adds reward and destroys the target object. Also adds to score for visual representation.
    /// </summary>
    /// <param name="other">The target</param>
    public void OnTriggerEnter(Collider other)
    {
        Debug.Log("Triggered by: " + other);
        AddReward(2f);
        score++;
        scoreText.text = tag + ": " + score;
        stageGenerator.RespawnTarget();
        targetPos = stageGenerator.TargetLocation;
    }

    /// <summary>
    /// All the float values that should be monitored by the neural network are listed here.
    /// </summary>
    public override void CollectObservations()
    {
        if (useVectorObs)
        {
            Debug.Log("Adding observations");
            AddVectorObs(transform.rotation.y);
            AddVectorObs(drone.velocity.x);
            AddVectorObs(drone.velocity.y);
            AddVectorObs(drone.velocity.z);
            AddVectorObs(Math.Abs(targetPos.x - transform.position.x));
            AddVectorObs(Math.Abs(targetPos.y - transform.position.y));
            AddVectorObs(Math.Abs(targetPos.z - transform.position.z));
        }
    }


    /// <summary>
    /// The actions invoked at every step of the brain. 
    /// This specific version translates the model outputs into movement.
    /// </summary>
    /// <param name="vectorAction"></param>
    /// <param name="textAction"></param>
    public override void AgentAction(float[] vectorAction, string textAction)
    {
        if (brain.brainParameters.vectorActionSpaceType == SpaceType.discrete)
        {
            rotation = Mathf.FloorToInt(vectorAction[0]);
            altitude = Mathf.FloorToInt(vectorAction[1]);
            frontal = Mathf.FloorToInt(vectorAction[2]);
            side = Mathf.FloorToInt(vectorAction[3]);

            MoveAgentFrontal(frontal);
            MoveAgentSide(side);
            MoveAgentAltitude(altitude);
            MoveAgentRotate(rotation);
        }


        //Small punishment for moving around without goal
        AddReward(-1f / agentParameters.maxStep);

        drone.rotation = Quaternion.Euler(new Vector3(0, yawForces.CurrentForce, 0));
        drone.AddRelativeForce(new Vector3(strafeForces.CurrentForce, altitudeForces.CurrentForce, velocityForces.CurrentForce));
    }

    private void MoveAgentFrontal(float act)
    {
        if (act == 1)
        {
            //Move forward
            Debug.Log("Moving forward");
            velocityForces.CurrentForce = velocityForces.CurrentForce + (velocityForces.PositiveAcceleration * Time.deltaTime);
            velocityForces.CurrentForce = Mathf.Clamp(velocityForces.CurrentForce, velocityForces.MinForce, velocityForces.MaxForce);
        }
        else if (act == 2)
        {
            //Move backward
            Debug.Log("Moving backward");
            velocityForces.CurrentForce = velocityForces.CurrentForce + (velocityForces.NegativeAcceleration * Time.deltaTime);
            velocityForces.CurrentForce = Mathf.Clamp(velocityForces.CurrentForce, velocityForces.MinForce, velocityForces.MaxForce);
        }
        else
        {
            //decelerate until stationary
            if (velocityForces.CurrentForce > 0)
            {
                velocityForces.CurrentForce = velocityForces.CurrentForce - (velocityForces.FrictionForce * Time.deltaTime);
                velocityForces.CurrentForce = Mathf.Clamp(velocityForces.CurrentForce, 0, velocityForces.MaxForce);
            }
            else
            {
                velocityForces.CurrentForce = velocityForces.CurrentForce + (velocityForces.FrictionForce * Time.deltaTime);
                velocityForces.CurrentForce = Mathf.Clamp(velocityForces.CurrentForce, velocityForces.MinForce, 0);
            }
        }
    }

    private void MoveAgentSide(float act)
    {
        if (act == 1)
        {
            //Strafe right
            Debug.Log("Strafe right");
            strafeForces.CurrentForce = strafeForces.CurrentForce + (strafeForces.PositiveAcceleration * Time.deltaTime);
            strafeForces.CurrentForce = Mathf.Clamp(strafeForces.CurrentForce, strafeForces.MinForce, strafeForces.MaxForce);

        }
        else if (act == 2)
        {
            //Strafe left
            Debug.Log("Strafe left");
            strafeForces.CurrentForce = strafeForces.CurrentForce + (strafeForces.NegativeAcceleration * Time.deltaTime);
            strafeForces.CurrentForce = Mathf.Clamp(strafeForces.CurrentForce, strafeForces.MinForce, strafeForces.MaxForce);
        }
        else
        {
            //Decelerating until stationary
            if (strafeForces.CurrentForce > 0)
            {
                strafeForces.CurrentForce = strafeForces.CurrentForce - (strafeForces.FrictionForce * Time.deltaTime);
                strafeForces.CurrentForce = Mathf.Clamp(strafeForces.CurrentForce, 0, strafeForces.MaxForce);
            }
            else
            {
                strafeForces.CurrentForce = strafeForces.CurrentForce + (strafeForces.FrictionForce * Time.deltaTime);
                strafeForces.CurrentForce = Mathf.Clamp(strafeForces.CurrentForce, strafeForces.MinForce, 0);
            }
        }
    }

    private void MoveAgentRotate(float act)
    {
        if (act == 1)
        {
            //Yaw rotate clockwise
            Debug.Log("Yaw rotation clockwise");
            yawForces.CurrentForce = yawForces.CurrentForce + (yawForces.PositiveAcceleration * Time.deltaTime);
            if (yawForces.CurrentForce == 360) yawForces.CurrentForce = 0;
        }
        else if (act == 2)
        {
            //Yaw rotate anti-clockwise
            Debug.Log("Yaw rotation anti-clockwise");
            yawForces.CurrentForce = yawForces.CurrentForce + (yawForces.NegativeAcceleration * Time.deltaTime);
            if (yawForces.CurrentForce == -360) yawForces.CurrentForce = 0;
        }
    }

    private void MoveAgentAltitude(float act)
    {
        if (act == 1)
        {
            //Ascend
            Debug.Log("Ascending...");
            altitudeForces.CurrentForce = altitudeForces.CurrentForce + (altitudeForces.PositiveAcceleration * Time.deltaTime);
            altitudeForces.CurrentForce = Mathf.Clamp(altitudeForces.CurrentForce, altitudeForces.MinForce, altitudeForces.MaxForce);

        }
        else if (act == 2)
        {
            //Descend
            Debug.Log("Descending...");
            altitudeForces.CurrentForce = altitudeForces.CurrentForce + (altitudeForces.NegativeAcceleration * Time.deltaTime);
            altitudeForces.CurrentForce = Mathf.Clamp(altitudeForces.CurrentForce, altitudeForces.MinForce, altitudeForces.MaxForce);
        }
        else
        {
            //decelerate until stationary
            if (altitudeForces.CurrentForce > 0)
            {
                altitudeForces.CurrentForce = altitudeForces.CurrentForce - (altitudeForces.FrictionForce * Time.deltaTime);
                altitudeForces.CurrentForce = Mathf.Clamp(altitudeForces.CurrentForce, 0, altitudeForces.MaxForce);
            }
            else
            {
                altitudeForces.CurrentForce = altitudeForces.CurrentForce + (altitudeForces.FrictionForce * Time.deltaTime);
                altitudeForces.CurrentForce = Mathf.Clamp(altitudeForces.CurrentForce, altitudeForces.MinForce, 0);
            }
        }
    }
}
