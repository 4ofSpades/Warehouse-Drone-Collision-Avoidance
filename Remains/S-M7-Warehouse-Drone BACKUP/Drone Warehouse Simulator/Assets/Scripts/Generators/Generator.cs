using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;

/// <summary>
/// Abstract class for creating a strategy design pattern for the implementation of the spawners
/// </summary>
public abstract class Generator : ScriptableObject
{
    protected List<GameObject> prefabParts;
    public bool isSpawned;
    public Transform parent;

    /// <summary>
    /// Add a reference to the prefab to the list so it can be instantiated within the code
    /// </summary>
    /// <param name="gameObjectName">The name of the prefab</param>
    protected void LoadPrefab(string gameObjectName)
    {
        if (prefabParts == null)
        {
            prefabParts = new List<GameObject>();
        }
        if (!prefabParts.Exists(p => p.name.Equals(gameObjectName)))
        {
            try
            {
                prefabParts.Add(Resources.Load<GameObject>(gameObjectName));
            }
            catch (System.Exception)
            {
                throw;
            }

        }
    }

    /// <summary>
    /// Helper method for finding GameObject objects by name
    /// </summary>
    /// <param name="gameObjects">The list containing the GameObject objects</param>
    /// <param name="name">The name of the desired object</param>
    /// <returns>A copy of the GameObject object containing the specified name</returns>
    protected GameObject GetGameObjectByName(List<GameObject> gameObjects, string name)
    {
        return gameObjects.Find(p => p.name.Equals(name));
    }

    public abstract void Spawn();
    public abstract void Despawn();


}