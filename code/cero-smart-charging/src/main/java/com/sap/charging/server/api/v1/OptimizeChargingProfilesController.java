package com.sap.charging.server.api.v1;

import com.sap.charging.model.ChargingStation;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.parameters.P;
import org.springframework.web.bind.annotation.CrossOrigin;


import java.net.URI;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.List;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;

import com.sap.charging.realTime.State;
import com.sap.charging.realTime.StrategyAlgorithmic;
import com.sap.charging.realTime.model.forecasting.departure.CarDepartureForecast;
import com.sap.charging.server.api.v1.store.OptimizerSettings;
import com.sap.charging.sim.Simulation;
import com.sap.charging.sim.event.Event;
import com.sap.charging.util.Loggable;

import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import io.swagger.annotations.ApiParam;
import org.springframework.web.client.RestTemplate;

@RestController
@Api(value = "emobility-smart-charging REST API")
public class OptimizeChargingProfilesController implements Loggable {

    @Override
    public int getVerbosity() {
        return Simulation.verbosity;
    }
    public StrategyAlgorithmic buildStrategy(OptimizerSettings settings, PricePowerLimits pLimits) {
        StrategyAlgorithmic s = buildStrategy(settings);
        s.setPricePowerLimits(pLimits);
        return s;
    }
    public StrategyAlgorithmic buildStrategy(OptimizerSettings settings) {
        StrategyAlgorithmic strategy = new StrategyAlgorithmic(CarDepartureForecast.getDefaultCarDepartureForecast());
        strategy.objectiveFairShare.setWeight(settings.getWeightObjectiveFairShare());
        strategy.objectiveEnergyCosts.setWeight(settings.getWeightObjectiveEnergyCosts());
        strategy.objectivePeakShaving.setWeight(settings.getWeightObjectivePeakShaving());
        strategy.objectiveLoadImbalance.setWeight(settings.getWeightObjectiveLoadImbalance());
        strategy.setReoptimizeOnStillAvailableAfterExpectedDepartureTimeslot(true);
        strategy.setRescheduleCarsWith0A(false);
        return strategy;
    }

    @CrossOrigin(origins = "*")
    @ApiOperation(value = "Optimize Charging Profiles")
    @PostMapping(path = "/api/v1/OptimizeChargingProfiles", produces = MediaType.APPLICATION_JSON_VALUE)
    @ResponseBody
    public ResponseEntity<Object> optimizeChargingProfiles(@ApiParam @RequestBody OptimizeChargingProfilesRequest request) {

        Simulation.verbosity = request.verbosity;

        log(0, "Received /api/v1/OptimizeChargingProfiles with body: " + request.toString() );
        log(1, "Using optimizer settings: " + request.optimizerSettings.toString());

        // Request values
        Object response = null;
        HttpStatus httpStatus = HttpStatus.ACCEPTED;
        try {
            State state = request.state.toState();
            Event event = request.event.toEvent(state);

            List<Double> priceArray = fetchPriceArray(request.priceSettings.priceServerUrl);
            int slots = state.energyPriceHistory.getNTimeslots();

            PricePowerLimits pLimits = new PricePowerLimits(request.priceSettings,priceArray,slots);

            // React to events
            StrategyAlgorithmic strategy = buildStrategy(request.optimizerSettings, pLimits);
            log(1, "Optimizer's sorting criteria (objective for cars above min SoC): " + strategy.getSortingCriteriaByObjective());

            strategy.react(state, event);

            // Create response
            response = new OptimizeChargingProfilesResponse(state.cars);
        } catch (Exception e) {
            System.err.println(e.getClass().getName());
            System.err.println(e.getMessage());
            response = new ErrorResponse(e);
            httpStatus = HttpStatus.INTERNAL_SERVER_ERROR;
            e.printStackTrace();
        }

        return new ResponseEntity<>(response, httpStatus);
    }

    private List<Double> fetchPriceArray(String priceServerUrl) throws Exception {
        LocalDate currentDate = LocalDate.now();
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("dd-MM-yyyy");
        String formattedDate = currentDate.format(formatter);
        return fetchPriceArray(priceServerUrl, formattedDate);
    }

    private List<Double> fetchPriceArray(String priceServerUrl, String date) throws Exception {
        String url = priceServerUrl + "/getPrices/" + date;

        RestTemplate restTemplate = new RestTemplate();
        ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);

        if (response.getStatusCode() != HttpStatus.OK) {
            throw new RuntimeException("Failed to fetch prices: HTTP " + response.getStatusCode());
        }

        ObjectMapper objectMapper = new ObjectMapper();
        PriceResponse priceResponse = objectMapper.readValue(response.getBody(), PriceResponse.class);
        return priceResponse.getPrices();
    }
}


