using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;
using Random = UnityEngine.Random;

class TargetGenerator : Generator
{
    private int amountOfTargets;
    private TargetSpawnMode mode;
    private Vector3 targetLocation;
    public Vector3 TargetLocation { get => targetLocation; }
    

    public enum TargetSpawnMode { SINGLE, BATCH }

    public TargetGenerator(int amountOftargets, TargetSpawnMode mode, Transform parent)
    {
        this.mode = mode;
        this.amountOfTargets = amountOftargets;
        this.parent = parent;
        LoadPrefab("Target");
    }

    public override void Despawn()
    {
        //TODO: don't destroy but move target
        if (targetLocation != null)
        {
            Destroy(GameObject.Find("Target"));
        }
    }

    public override void Spawn()
    {
        if (mode == TargetSpawnMode.SINGLE)
        {
            SpawnSingleTarget();
        }
    }

    /// <summary>
    /// Spawns a single target
    /// </summary>
    private void SpawnSingleTarget()
    {
        GameObject interior = GameObject.Find("Interior");
        //string tag = "Target Spawn Empty";

        ////Assign absolute location if no racks are spawned 
        //bool worldPosStay = true;
        //Vector3 localScale = new Vector3(1 / 21f, 1 / 7.5f, 1 / 15f);

        //if (interior.transform.childCount > 0)
        //{
        string tag = "Target Spawn Rack";
        Vector3 localScale = new Vector3(1 / 4.5f, 1 / 7.5f, 0.5f);
        bool worldPosStay = false;
        //}
        GameObject[] locations = GameObject.FindGameObjectsWithTag(tag);
        locations = locations.Where(l => l.transform.IsChildOf(parent)).ToArray();
        GameObject target = Instantiate(GetGameObjectByName(prefabParts, "Target"), locations[Random.Range(0, locations.Length)].transform, worldPosStay);
        target.transform.localPosition = new Vector3(Random.Range(-0.5f, 0.5f), Random.Range(-0.5f, 0.5f), Random.Range(-0.5f, 0.5f));
        target.transform.localScale = localScale;
        targetLocation = target.transform.position;
        target.name = "Target";
    }
}
