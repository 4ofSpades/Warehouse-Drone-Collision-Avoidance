def smooth(scalars, weight: float):  # Weight between 0 and 1
    last = scalars[0]  # First value in the plot (first timestep)
    smoothed = list()
    for point in scalars:
        smoothed_val = last * weight + (1 - weight) * point  # Calculate smoothed value
        smoothed.append(smoothed_val)                        # Save it
        last = smoothed_val                                  # Anchor the last smoothed value

    return smoothed

if __name__ == "__main__":
    scalars_up = [166,166,165,167,167,170,170,168,168,169,169,164,164,165,167,295,295,294,294,165,165]
    scalars_down = []
    mean = sum(scalars_up) / len(scalars_up)
    print(mean)
    weight = 0.2
    print(smooth(scalars_up, weight))