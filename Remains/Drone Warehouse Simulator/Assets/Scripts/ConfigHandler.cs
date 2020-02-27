using Newtonsoft.Json;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Runtime.Serialization;
using System.Runtime.Serialization.Json;
using UnityEngine;

/// <summary>
/// Class that reads a config JSON file containing variables that need to be communicated externally or that need a lot of adjustment. 
/// The class creates a default config file if none exists.
/// </summary>
public class ConfigHandler : MonoBehaviour
{
    [DataContract]
#pragma warning disable CS0649
    internal class Config
    {
        [DataMember]
        internal readonly bool isTraining;
        [DataMember]
        internal readonly int minAmountMidParts;
        [DataMember]
        internal readonly int maxAmountMidParts;
        [DataMember]
        internal readonly int randomPercentRacks;
    }

    private Config config;

    void Awake()
    {
        try
        {
            config = JsonConvert.DeserializeObject<Config>(System.IO.File.ReadAllText("config.json"));
        }
        catch (FileNotFoundException m)
        {
            //Fall back to defaults
            Debug.LogWarning(m.Message + "| Using defaults...");
            config = JsonConvert.DeserializeObject<Config>(@"{'isTraining': true,'minAmountMidParts': 1," + 
                @"'maxAmountMidParts': 8, 'randomPercentRacks': 80}");
        }
    }

    public bool IsTraining { get => config.isTraining; }

    public int MinAmountMidParts { get => config.minAmountMidParts; }

    public int MaxAmountMidParts { get => config.maxAmountMidParts; }

    public int RandomPercentRacks { get => config.randomPercentRacks; }
}
