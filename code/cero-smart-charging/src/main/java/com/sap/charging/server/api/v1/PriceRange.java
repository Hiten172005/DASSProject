package com.sap.charging.server.api.v1;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;

import static java.lang.Math.max;

public class PriceRange {
    public double startPrice;
    public double maxCurrent;
    @JsonCreator
    public PriceRange(@JsonProperty(value = "startPrice",required = true) double startPrice, @JsonProperty(value = "maxCurrent",required = true) double maxCurrent) {
        this.startPrice = startPrice;
        this.maxCurrent = max(maxCurrent,0);
    }
}


