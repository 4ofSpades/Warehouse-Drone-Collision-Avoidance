using System.Collections;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// Class that obtains and holds the config info to ensure consistency among multiple player areas
/// </summary>
public class GameInitializer : MonoBehaviour
{
    //Config vars
    ConfigHandler configHandler;
    private int minAmountMidParts;
    private int maxAmountMidParts;
    private int randomPercentRacks;
    private bool isTraining;
    private int amountOfTargets;

    private int amountMidParts;

    public bool IsTraining { get => isTraining; }
    public int RandomPercentRacks { get => randomPercentRacks; }
    public int MaxAmountMidParts { get => maxAmountMidParts; }
    public int MinAmountMidParts { get => minAmountMidParts; }
    public int AmountMidParts { get => amountMidParts; }
    public int AmountOfTargets { get => amountOfTargets; }

    void Awake()
    {
        GetConfig();
    }

    private void GetConfig()
    {
        configHandler = GetComponentInParent<ConfigHandler>();
        isTraining = configHandler.IsTraining;
        minAmountMidParts = configHandler.MinAmountMidParts;
        maxAmountMidParts = configHandler.MaxAmountMidParts;
        if (minAmountMidParts < 1) minAmountMidParts = 2;
        if (maxAmountMidParts < minAmountMidParts) maxAmountMidParts = minAmountMidParts;
        amountMidParts = UnityEngine.Random.Range(minAmountMidParts, maxAmountMidParts);
        randomPercentRacks = Mathf.Clamp(configHandler.RandomPercentRacks, 0, 100);

        if (amountOfTargets < 1 || amountOfTargets > amountMidParts)
        {
            amountOfTargets = 1;
        }
    }


}
