import React from "react";
import '../RangeGraph.css'

import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import {procentage} from "../utils";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const labels = Array.from({ length: 13 }, (_, i) => i*5);

const findClosestLabel = (num) => {
    let lastDiff = 999;
    let closest = labels[0];

    for (let l of labels) {
        const diff = Math.abs(l - num);
        if (diff < lastDiff) {
            lastDiff = diff;
            closest = l;
        }
    }
    return closest
}

const processData = (data) => {
    let ndata = {};

    for (const l of labels)
        ndata[l] = [0,0,0];

    data.filter(item => item.weapon_type === 'A/A' && item.range !== null && item.range !== -1).forEach(item => {
        const label = findClosestLabel(item.range);
        ndata[label][0] += item.qty;
        if (item.hit || item.destroyed)
            ndata[label][1] += item.qty;
    })
    let entries = Object.entries(ndata);
    entries.forEach((entry) => {
        ndata[entry[0]][2] = procentage(entry[1][1], entry[1][0]);
    })
    return ndata;
}

const calculateEff = (entries) => {
    let effs = [];
    let peak = 0;
    let peakShots = 0;
    let total_shots = 0;
    entries.forEach(entry => total_shots += entry[1][0]);

    entries.forEach(entry => {
        const eff = entry[1][1]/total_shots;
        if (eff > peak)
            peak = eff;
        if (entry[1][0] > peakShots)
            peakShots = entry[1][0]
        effs.push(eff);
    })

    const n = peakShots*1.25 / peak;
    effs = effs.map(i => i*n);

    return effs;
}

const RangeGraph = ({data}) => {
    const stats = processData(data);
    const pkStats = Object.entries(stats).map(item => item[1][2]);
    const killStats = Object.entries(stats).map(item => item[1][1]);
    const shotsStats = Object.entries(stats).map(item => item[1][0]);
    const efficiencyCoeff = calculateEff(Object.entries(stats));

    const chartData = {
        labels,
        datasets: [
            {
                label: 'Kills',
                data: killStats,
                fill: false,
                backgroundColor: 'rgb(133,30,30)',
                borderColor: 'rgb(255,86,86)',
                tension: 0.3, // Makes the line smooth
                hidden: true
            }
,
            {
                label: 'Shots',
                data: shotsStats,
                fill: false,
                backgroundColor: 'rgb(30,37,133)',
                borderColor: 'rgb(86,114,255)',
                tension: 0.3, // Makes the line smooth
                hidden: false
            },
            {
                label: 'PK%',
                data: pkStats,
                fill: false,
                backgroundColor: 'rgb(104,30,133)',
                borderColor: 'rgb(235,86,255)',
                tension: 0.3, // Makes the line smooth
                hidden: true
            },
            {
                label: 'efficiency',
                data: efficiencyCoeff,
                fill: false,
                backgroundColor: 'rgb(59,133,30)',
                borderColor: 'rgb(134,255,86)',
                tension: 0.3, // Makes the line smooth
                hidden: false
            }
            ]
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: false,
            }
        },
        scales: {
            x: {
                title: {
                    display: true,
                    text: 'range'
                }
            },
            y: {
                title: {
                    display: false,
                    text: ''
                },
                beginAtZero: true // Start y-axis at 0
            }
        }
    };

    return (
        <div className="App-RangeChart">
            <Line data={chartData} options={options} />
        </div>
    )
}

export default RangeGraph