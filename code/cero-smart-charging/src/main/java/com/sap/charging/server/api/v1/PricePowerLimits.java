package com.sap.charging.server.api.v1;

import com.sap.charging.model.EnergyUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Arrays;
import java.util.List;

public class PricePowerLimits
{
    private static final Logger log = LoggerFactory.getLogger(PricePowerLimits.class);
    public double[] phaseLimits;
    private int slots;
    public PricePowerLimits(PriceSettings ps, List<Double> actualPrices, int slots){
        phaseLimits = new double[slots];
        for (int i = 0; i < slots; i++) {
            phaseLimits[i] = Double.POSITIVE_INFINITY;
        }
        for(int i=0;i<Math.min(actualPrices.size(),slots);i++){
            double price = actualPrices.get(i);
            for(PriceRange pr: ps.ranges){
                if(price > pr.startPrice){
                   phaseLimits[i] = pr.maxCurrent/3; // assuming 3 phases for now, can be changed later.
                    break;
                }
            }
        }
        this.slots = slots;
    }
    public PricePowerLimits(){
        phaseLimits = new double[96];
        for (int i = 0; i < 96; i++) {
            phaseLimits[i] = Double.POSITIVE_INFINITY;
        }
    }
    public double getMaxPhaseCurrent(int slot){
        if(slot<0||slot>=slots)
            return Double.POSITIVE_INFINITY;
        return phaseLimits[slot];
    }
}
