package com.sap.charging.server.api.v1;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;

public class PriceResponse {
    public final List<Double> prices;
    @JsonCreator
    public PriceResponse(@JsonProperty("prices")  List<Double> prices) {
        this.prices = prices;
    }

    public List<Double> getPrices() {
        return prices;
    }
}
