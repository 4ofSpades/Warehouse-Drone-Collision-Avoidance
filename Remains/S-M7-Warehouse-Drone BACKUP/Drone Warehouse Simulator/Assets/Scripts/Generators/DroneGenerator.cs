using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;
using Random = UnityEngine.Random;

class DroneGenerator : Generator
{
    GameObject drone;

    public DroneGenerator(Transform parent)
    {
        //LoadPrefab("Seacon Drone Variant");
        this.parent = parent;
    }

    public override void Despawn()
    {
        return;
    }

    /// <summary>
    /// Spawn the drone within warehouse without it getting stuck in a wall
    /// </summary>
    public override void Spawn()
    {
        //Define the smallest and largest vector3 coordinates
        //float x = Random.Range(parent.position.x + -7f, parent.position.x + 7f);
        //float y = Random.Range(parent.position.y + 0.5f, parent.position.y + 2f);
        //float z = Random.Range(parent.position.z + 3f, parent.position.z + 10f);
        float x = parent.position.x;
        float y = parent.position.y - 4;
        float z = parent.position.z;

        drone = GameObject.FindGameObjectWithTag(parent.tag);
        if (!drone)
        {
            drone = Instantiate(GetGameObjectByName(prefabParts, "Seacon Drone Variant"),
                new Vector3(x, y, z),
                Quaternion.Euler(0, 0, 0),
                parent);
            drone.name = "Seacon Drone";
            drone.transform.Find("LED").GetComponent<Renderer>().material.SetColor("_Color", Color.red);
        }
        else
        {
            drone.transform.position = new Vector3(x, y, z);
        }
    }
}

