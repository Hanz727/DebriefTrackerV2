import React, {useEffect, useState} from "react";
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import {procentage} from "../utils";
import '../KillChartStats.css'

// Register chart.js components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

function getWeekNumber(date) {
    const firstDayOfYear = new Date(date.getFullYear(), 0, 1); // January 1st of the year
    const pastDaysOfYear = (date - firstDayOfYear) / 86400000; // Days passed since the first day of the year

    return Math.ceil((pastDaysOfYear + firstDayOfYear.getDay() + 1) / 7);
}

const processData = (data) => {
    const shotsPerDate = {};
	const killsPerDate = {};
    data.filter((item) => item.weapon_type === 'A/A').forEach(item => {
        const date = new Date(item.date);
        const month = `Week ${getWeekNumber(date)} ${date.getFullYear()}`; // Format as MM/YYYY

		if (!(month in shotsPerDate)) {
            shotsPerDate[month] = 0;
        }
		if (!(month in killsPerDate)) {
            killsPerDate[month] = 0;
        }
        shotsPerDate[month] += item.qty;
		if (item.hit || item.destroyed) {
			killsPerDate[month] += item.qty;
		}

    });

    return [shotsPerDate, killsPerDate];
}

const KillChartStats = ({data}) => {
    const [shotsPerDate, killsPerDate] = processData(data);

	const labels = Object.keys(shotsPerDate).reverse();
    const killsData = Object.values(killsPerDate).reverse();
    const shotsData = Object.values(shotsPerDate).reverse();

    let accData = shotsData;
    accData = accData.map((value, index) => {
        return value - killsData[index];
    })

    let accpData = shotsData;
    accpData = accpData.map((value, index) => {
        return procentage(killsData[index], value);
    })

    const chartData = {
        labels,
        datasets: [
            {
                label: 'Kills',
                data: killsData,
                fill: false,
                backgroundColor: 'rgb(133,30,30)',
                borderColor: 'rgb(255,86,86)',
                tension: 0.3 // Makes the line smooth
            },
            {
                label: 'Shots',
                data: shotsData,
                fill: false,
                backgroundColor: 'rgb(30,37,133)',
                borderColor: 'rgb(86,114,255)',
                tension: 0.3 // Makes the line smooth
            },
            {
                label: 'Misses',
                data: accData,
                fill: false,
                backgroundColor: 'rgb(59,133,30)',
                borderColor: 'rgb(97,255,86)',
                tension: 0.3, // Makes the line smooth
                hidden: true
            },
            {
                label: 'PK%',
                data: accpData,
                fill: false,
                backgroundColor: 'rgb(104,30,133)',
                borderColor: 'rgb(235,86,255)',
                tension: 0.3, // Makes the line smooth
                hidden: true
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
                    display: false,
                    text: ''
                },
				ticks: {
                    // Customize the label display
                    callback: function(value, index, ticks) {
                        // Show every 2nd label (you can change the number to 3 for every third label)
						let d = Math.round(1/ (12 / labels.length));
						if (d === 0)
							d = 1;
                        return index % d === 0 ? this.getLabelForValue(value) : '';
                    }
                }
            },
            y: {
                title: {
                    display: true,
                    text: ''
                },
                beginAtZero: true // Start y-axis at 0
            }
        }
    };

    return (
        <div className="App-KillChart">
            <Line data={chartData} options={options} />
        </div>
    );
}

export default KillChartStats