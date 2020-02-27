using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class HoverDrone : MonoBehaviour {

    public float horizontalSpeed;
    public float verticalSpeed;
    public float amplitude;
    public Vector3 deltaPosition;
    public Vector3 currentPosition;

    public float yRotation = 0F;



	// Use this for initialization
	void Start () {
        currentPosition = transform.position;
	}
	
	// Update is called once per frame
	void FixedUpdate () {


        deltaPosition.x = Mathf.Sin(Time.realtimeSinceStartup * horizontalSpeed) * amplitude;;
        deltaPosition.y = Mathf.Sin(Time.realtimeSinceStartup * verticalSpeed) * amplitude;
        deltaPosition.z = Mathf.Cos(Time.realtimeSinceStartup * horizontalSpeed) * amplitude;

        yRotation = Mathf.Cos(Time.realtimeSinceStartup * horizontalSpeed) * amplitude * 50;



        transform.position = currentPosition + deltaPosition;
        transform.eulerAngles = new Vector3(0, yRotation, 0);
	}
}
