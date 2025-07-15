package com.sap.charging.server.api.v1;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;


import java.util.Arrays;
import java.util.List;

public class PriceSettings {
    public final List<PriceRange> ranges;
    public final String priceServerUrl;

    @JsonCreator
    public PriceSettings(@JsonProperty(value = "ranges", required = true) List<PriceRange> ranges, @JsonProperty(value = "priceServerUrl",required = true) String priceServerUrl) {
        if (ranges != null) {
            // descending sort.
            ranges.sort((r1, r2) -> Double.compare(r2.startPrice, r1.startPrice));

            // Extend the last price to 0 if the last price's startPrice is greater than 0
            PriceRange lastRange = ranges.get(ranges.size() - 1);
            if (lastRange.startPrice > 0) {
                ranges.add(new PriceRange(0, lastRange.maxCurrent));
            }
        }
        // if last price greater than 0, then extend the same maxKW to 0
        
        this.ranges = ranges;
        this.priceServerUrl = priceServerUrl;
    }

    public static PriceSettings getDefaultPriceSettings() {
        return new PriceSettings(
                Arrays.asList(
                        new PriceRange(0, 40),
                        new PriceRange(10, 30),
                        new PriceRange(15, 25),
                        new PriceRange(20, 20)
                ),
                "http://localhost:3000"
        );
    }
}
