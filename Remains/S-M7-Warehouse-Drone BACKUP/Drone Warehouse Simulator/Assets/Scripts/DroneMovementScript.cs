using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// Script for controlling the drone model using the following keys:
/// Increase altitude = I
/// Decrease altitude = K
/// Move forwards = W
/// Move backwards = S
/// Rotate clockwise = E
/// Rotate anti-clockwise = Q
/// Strafe right = D
/// Strafe left = A
/// </summary>
public class DroneMovementScript : MonoBehaviour
{
    //Variable to store the drone entity in
    Rigidbody drone;

    public struct PositioningForces
    {
        //Terminal velocities
        private readonly float minForce, maxForce;
        //The current speed
        private float currentForce;
        //How fast an object should increase speed towards one side and its opposite side
        private readonly float negativeAcceleration, positiveAcceleration;
        //How fast a moving object should go stationary when not putting in any controls
        private readonly float frictionForce;

        //Properties
        public float MinForce
        {
            get
            {
                return minForce;
            }
        }

        public float MaxForce
        {
            get
            {
                return maxForce;
            }
        }

        public float CurrentForce
        {
            get
            {
                return currentForce;
            }
            set
            {
                currentForce = value;
            }
        }

        public float NegativeAcceleration
        {
            get
            {
                return negativeAcceleration;
            }
        }

        public float PositiveAcceleration
        {
            get
            {
                return positiveAcceleration;
            }
        }

        public float FrictionForce
        {
            get
            {
                return frictionForce;
            }
        }

        public PositioningForces(float minForce, float maxForce, float currentForce, float negativeAcceleration, 
            float positiveAcceleration, float frictionForce)
        {
            this.minForce = minForce;
            this.maxForce = maxForce;
            this.currentForce = currentForce;
            this.negativeAcceleration = negativeAcceleration;
            this.positiveAcceleration = positiveAcceleration;
            this.frictionForce = frictionForce;
        }
    };

    public PositioningForces altitude = new PositioningForces(-4, 4, 0, -8, 8, 8);
    public PositioningForces velocity = new PositioningForces(-10, 10, 0, -5, 5, 10);
    public PositioningForces strafe = new PositioningForces(-5, 5, 0, -10, 10, 10);
    public PositioningForces yaw = new PositioningForces(-360, 360, 0, -45, 45, 180);

    private void Awake()
    {
        drone = GetComponent<Rigidbody>();
    }

    void Update()
    {
        MovementUpDown();
        MovementForwardBackward();
        MovementYaw();
        MovementStrafe();
        drone.transform.localRotation = Quaternion.Euler(new Vector3(0, yaw.CurrentForce, 0));
    }

    void FixedUpdate()
    {

        drone.rotation = Quaternion.Euler(new Vector3(0, yaw.CurrentForce, 0));
        drone.AddRelativeForce(new Vector3(strafe.CurrentForce, altitude.CurrentForce, velocity.CurrentForce));
        
    }

    private void MovementForwardBackward()
    {
        if (Input.GetKey(KeyCode.W))
        {
            //Move forward
            Debug.Log("Moving forward");
            velocity.CurrentForce = velocity.CurrentForce + (velocity.PositiveAcceleration * Time.deltaTime);
            velocity.CurrentForce = Mathf.Clamp(velocity.CurrentForce, velocity.MinForce, velocity.MaxForce);
        }
        else if (Input.GetKey(KeyCode.S))
        {
            //Move backward
            Debug.Log("Moving backward");
            velocity.CurrentForce = velocity.CurrentForce + (velocity.NegativeAcceleration * Time.deltaTime);
            velocity.CurrentForce = Mathf.Clamp(velocity.CurrentForce, velocity.MinForce, velocity.MaxForce);
        }
        else
        {
            //decelerate until stationary
            if (velocity.CurrentForce > 0)
            {
                velocity.CurrentForce = velocity.CurrentForce - (velocity.FrictionForce * Time.deltaTime);
                velocity.CurrentForce = Mathf.Clamp(velocity.CurrentForce, 0, velocity.MaxForce);
            }
            else
            {
                velocity.CurrentForce = velocity.CurrentForce + (velocity.FrictionForce * Time.deltaTime);
                velocity.CurrentForce = Mathf.Clamp(velocity.CurrentForce, velocity.MinForce, 0);
            }
        }
    }

    private void MovementUpDown()
    {
        if (Input.GetKey(KeyCode.I))
        {
            //Ascend
            Debug.Log("Ascending...");
            altitude.CurrentForce = altitude.CurrentForce + (altitude.PositiveAcceleration * Time.deltaTime);
            altitude.CurrentForce = Mathf.Clamp(altitude.CurrentForce, altitude.MinForce, altitude.MaxForce);

        }
        else if (Input.GetKey(KeyCode.K))
        {
            //Descend
            Debug.Log("Descending...");
            altitude.CurrentForce = altitude.CurrentForce + (altitude.NegativeAcceleration * Time.deltaTime);
            altitude.CurrentForce = Mathf.Clamp(altitude.CurrentForce, altitude.MinForce, altitude.MaxForce);
        }
        else
        {
            //decelerate until stationary
            if (altitude.CurrentForce > 0)
            {
                altitude.CurrentForce = altitude.CurrentForce - (altitude.FrictionForce * Time.deltaTime);
                altitude.CurrentForce = Mathf.Clamp(altitude.CurrentForce, 0, altitude.MaxForce);
            }
            else
            {
                altitude.CurrentForce = altitude.CurrentForce+ (altitude.FrictionForce * Time.deltaTime);
                altitude.CurrentForce = Mathf.Clamp(altitude.CurrentForce, altitude.MinForce, 0);
            }
        }
    }

    private void MovementYaw()
    {
        if (Input.GetKey(KeyCode.E))
        {
            //Yaw rotate clockwise
            Debug.Log("Yaw rotation clockwise");
            yaw.CurrentForce = yaw.CurrentForce + (yaw.PositiveAcceleration * Time.deltaTime);
            if (yaw.CurrentForce == 360) yaw.CurrentForce = 0;
        }
        else if (Input.GetKey(KeyCode.Q))
        {
            //Yaw rotate anti-clockwise
            Debug.Log("Yaw rotation anti-clockwise");
            yaw.CurrentForce = yaw.CurrentForce + (yaw.NegativeAcceleration * Time.deltaTime);
            if (yaw.CurrentForce == -360) yaw.CurrentForce = 0;
        }
    }

    private void MovementStrafe()
    {
        if (Input.GetKey(KeyCode.D))
        {
            //Strafe right
            Debug.Log("Striding right");
            strafe.CurrentForce = strafe.CurrentForce + (strafe.PositiveAcceleration * Time.deltaTime);
            strafe.CurrentForce = Mathf.Clamp(strafe.CurrentForce, strafe.MinForce, strafe.MaxForce);

        }
        else if (Input.GetKey(KeyCode.A))
        {
            //Strafe left
            Debug.Log("Striding left");
            strafe.CurrentForce = strafe.CurrentForce + (strafe.NegativeAcceleration * Time.deltaTime);
            strafe.CurrentForce = Mathf.Clamp(strafe.CurrentForce, strafe.MinForce, strafe.MaxForce);
        }
        else
        {
            //Decelerating until stationary
            if(strafe.CurrentForce > 0)
            {
                strafe.CurrentForce = strafe.CurrentForce - (strafe.FrictionForce * Time.deltaTime);
                strafe.CurrentForce = Mathf.Clamp(strafe.CurrentForce, 0, strafe.MaxForce);
            }
            else
            {
                strafe.CurrentForce = strafe.CurrentForce + (strafe.FrictionForce * Time.deltaTime);
                strafe.CurrentForce = Mathf.Clamp(strafe.CurrentForce, strafe.MinForce, 0);
            }
        }
    }
}
