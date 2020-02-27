using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;

/// <summary>
/// Main class that creates a composition of all other generators. It also serves to abstractify the generation from the academy
/// </summary>
class StageGenerator : MonoBehaviour
{
    //TODO: Change name to StageInitializer to avoid naming convention inconsistencies
    //Generators
    public WarehouseGenerator environmentGenerator;
    public DroneGenerator playerGenerator;
    public TargetGenerator targetGenerator;

    //Config vars
    public int randomPercentRacks;
    public bool isTraining;

    //Shared vars
    public int amountOfTargets;
    public int amountMidParts;
    private Vector3 targetLocation;

    public Vector3 TargetLocation { get => targetLocation; }

    public void Awake()
    {
        GameInitializer gameInit = GetComponentInParent<GameInitializer>();
        this.amountMidParts = gameInit.AmountMidParts;
        this.isTraining = gameInit.IsTraining;
        this.randomPercentRacks = gameInit.RandomPercentRacks;
        this.amountOfTargets = gameInit.AmountOfTargets;
        environmentGenerator = new WarehouseGenerator(amountMidParts, randomPercentRacks, isTraining, transform);
        targetGenerator = new TargetGenerator(amountOfTargets, TargetGenerator.TargetSpawnMode.SINGLE, transform);
        playerGenerator = new DroneGenerator(transform);

        //The spawn order needs to be in the following order:
        RespawnEnvironment();
        RespawnTarget();
        RespawnPlayer();
    }

    public void Start()
    {


        
    }

    public void RespawnEnvironment()
    {
        environmentGenerator.Spawn();
    }

    /// <summary>
    /// The player doesn't need to be destroyed, only repositioned
    /// </summary>
    public void RespawnPlayer()
    {
        playerGenerator.Spawn();
    }

    public void RespawnTarget()
    {
        targetGenerator.Despawn();
        targetGenerator.Spawn();
        targetLocation = targetGenerator.TargetLocation;
    }
}
