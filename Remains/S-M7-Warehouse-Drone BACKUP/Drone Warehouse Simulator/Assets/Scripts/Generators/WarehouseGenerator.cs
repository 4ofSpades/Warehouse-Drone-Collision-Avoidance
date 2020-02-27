using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;
using Random = UnityEngine.Random;

/// <summary>
/// Concrete implementation of Generator class that provides generator functionality for the warehouse and its interior
/// </summary>
class WarehouseGenerator : Generator
{
    private int amountMidParts, randomPercentRacks;
    private bool isTraining;
    private string hideTag;

    //Roots children
    GameObject building;
    GameObject warehouseLocations;
    //GameObject interior;
    private bool isStageGenerated;

    /// <summary>
    /// Constructor
    /// </summary>
    /// <param name="amountMidParts">The size of the warehouse (Note: the warehouse will always containing a start and end part)</param>
    /// <param name="randomPercentRacks">The chance for a rack to spawn</param>
    /// <param name="isTraining">Enables/disables a training mode that is low cost</param>
    public WarehouseGenerator(int amountMidParts, int randomPercentRacks, bool isTraining, Transform parent)
    {
        this.amountMidParts = amountMidParts;
        this.randomPercentRacks = randomPercentRacks;
        this.isTraining = isTraining;

        hideTag = "Training";
        if (isTraining)
        {
            hideTag = "Model";
        }

        //Initializing direct children
        this.parent = parent;
        building = new GameObject("Building");
        building.transform.parent = this.parent;
        warehouseLocations = new GameObject("Warehouse Locations");
        warehouseLocations.transform.parent = this.parent;
        //interior = new GameObject("Interior");
        //interior.transform.parent = root.transform;
    }

    public override void Despawn()
    {
        for (int i = 0; i < building.transform.childCount; i++)
        {
            GameObject.Destroy(building.transform.GetChild(i).gameObject);
            if (warehouseLocations.transform.childCount > i)
            {
                GameObject.Destroy(warehouseLocations.transform.GetChild(i).gameObject);
            }
            //if (interior.transform.childCount > i)
            //{
            //    GameObject.Destroy(interior.transform.GetChild(i).gameObject);
            //}
        }
    }

    public override void Spawn()
    {
        if (isStageGenerated)
        {
            Despawn();
        }
        SpawnLocations();
        SpawnStructure();
        //SpawnInterior();
        isStageGenerated = true;
    }

    /// <summary>
    /// Generates empty objects with transforms containing the locations where the warehouse parts should be generated.
    /// </summary>
    private void SpawnLocations()
    {
        //Base for z coordinate (first part start at 10 because it is rotated 180 degrees)
        int z = 10;

        //Create x new transforms where x = length, and add to array
        for (int i = 0; i < amountMidParts + 1; i++)
        {
            GameObject location = new GameObject("Location " + i.ToString());
            location.transform.parent = warehouseLocations.transform;
            location.transform.position = new Vector3(parent.position.x, parent.position.y, parent.position.z + z);
            z += 10;
        }
    }

    /// <summary>
    /// Generates the warehouse structure with a starting and ending part.
    /// </summary>
    private void SpawnStructure()
    {

        //Obtain prefabs
        LoadPrefab("EdgeDoor Variant");
        LoadPrefab("Mid Variant");

        //First edge
        GameObject start = Instantiate(GetGameObjectByName(prefabParts, "EdgeDoor Variant"),
            warehouseLocations.transform.Find("Location 0").transform.position,
            Quaternion.Euler(0, 180, 0),
            building.transform) as GameObject;
        start.name = "Start";

        //Main part
        for (int i = 0; i < amountMidParts; i++)
        {
            GameObject mid = Instantiate(GetGameObjectByName(prefabParts, "Mid Variant"),
                warehouseLocations.transform.Find("Location " + i).transform.position,
                Quaternion.Euler(0, 0, 0),
                building.transform) as GameObject;
            mid.name = "Mid " + i.ToString();
        }

        //Last edge
        GameObject end = Instantiate(GetGameObjectByName(prefabParts, "EdgeDoor Variant"),
            warehouseLocations.transform.Find("Location " + amountMidParts).transform.position,
            Quaternion.Euler(0, 0, 0),
            building.transform) as GameObject;
        end.name = "End";

        foreach (var item in GameObject.FindGameObjectsWithTag(hideTag))
        {
            item.SetActive(false);
        }
    }

    ///// <summary>
    ///// Spawns the interior racks with small variance
    ///// </summary>
    //private void SpawnInterior()
    //{
    //    Debug.Log("Spawning interior");
    //    //Obtain reference of certain rack prefab variant with colliders
    //    LoadPrefab("Dual Rack");

    //    //Spawn racks for all places but the start and end
    //    for (int i = 0; i < amountMidParts; i++)
    //    {
    //        //10% chance for interior object to not spawn
    //        int x = Random.Range(1, 100);
    //        if (x <= randomPercentRacks)
    //        {
    //            GameObject rack = Instantiate(GetGameObjectByName(prefabParts, "Dual Rack"),
    //                warehouseLocations.transform.Find("Location " + (i + 1)).transform.position,
    //                Quaternion.Euler(0, 0, 0),
    //                interior.transform) as GameObject;
    //            rack.name = "Rack " + i.ToString();
    //        }
    //    }
    //}
}

