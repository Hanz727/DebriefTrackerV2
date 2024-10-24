import React from "react";
import '../LeaderboardGraph.css'

import { Bar } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';

// Register the necessary Chart.js components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);


const processData = (data) => {
    let kpp = {};
    data.filter(entry => entry.weapon_type === "A/A" && (entry.hit || entry.destroyed)).forEach(entry => {
        if (!(entry.pilot_name in kpp))
            kpp[entry.pilot_name] = 0;
        kpp[entry.pilot_name] += entry.qty;
        if (entry.rio_name === null) return;

        if (!(entry.rio_name in kpp))
            kpp[entry.rio_name] = 0;
        kpp[entry.rio_name] += entry.qty;
    })
    kpp = Object.fromEntries(Object.entries(kpp).sort(([, a], [, b]) => a - b).reverse());

    return kpp;
}

const LeaderboardGraph = ({data}) => {
    const stats = processData(data);
    const labels = Object.keys(stats);
    const kills = Object.values(stats);

    const colors = [
        'rgba(255, 99, 132, 0.6)',
        'rgba(54, 162, 235, 0.6)',
        'rgba(255, 206, 86, 0.6)',
        'rgba(75, 192, 192, 0.6)',
        'rgba(153, 102, 255, 0.6)',
        'rgba(255, 159, 64, 0.6)',
        'rgba(99, 255, 132, 0.6)'
    ];

    const barData = {
        labels: labels, // Labels for each section
        datasets: [
            {
                backgroundColor: colors,
                data: kills, // Data values corresponding to the labels
            },
        ],
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false,
            },
            title: {
                display: false,
            }
        },
        scales: {
            x: {
                title: {
                    display: false,
                }
            },
            y: {
                title: {
                    display: true,
                    text: 'Kills'
                },
                beginAtZero: true // Start y-axis at 0
            }
        }
    };

    return (
        <div className="App-LeaderboardGraph">
            <Bar data={barData} options={options} />
        </div>
    )
}

export default LeaderboardGraph