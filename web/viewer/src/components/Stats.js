import React, {useEffect} from "react";
import '../Stats.css'
import PerWeaponStats from "./PerWeaponStats";
import StatsBox from "./StatsBox";
import PerTargetStats from "./PerTargetStats";
import KillChartStats from "./KillChartStats";
import RangeGraph from "./RangeGraph";
import LeaderboardGraph from "./LeaderboardGraph";

const Stats = ({data}) => {
    return (
        <div>
            <div className="App-Stats-1">
                <StatsBox title="A/A Weapon Stats" style={{flexShrink:'0'}}>
                    <PerWeaponStats data={data} type="A/A"/>
                </StatsBox>

                <StatsBox title="A/G Weapon Stats" style={{flexShrink:'0'}}>
                    <PerWeaponStats data={data} type="A/G"/>
                </StatsBox>

                <StatsBox title="Per Target Stats" style={{flexShrink:'0'}}>
                    <PerTargetStats data={data}/>
                </StatsBox>

                <StatsBox title="Deployment Timeline"
                          style={{
                              flex: '1',
                              marginRight: '0',
                              minWidth: '370px',
                              display: 'flex',
                              flexDirection: 'column'
                          }}>
                    <KillChartStats data={data}/>
                </StatsBox>
            </div>

            <div className="App-Stats-2">
                <StatsBox title="Range graph"
                          style={{
                              flex: '1',
                              minWidth: '370px',
                              display: 'flex',
                              flexDirection: 'column',
                              minHeight: '300px',
                }}>
                    <RangeGraph data={data}/>
                </StatsBox>

                <StatsBox title="Leaderboard"
                          style={{
                              flex: '1',
                              minWidth: '370px',
                              display: 'flex',
                              flexDirection: 'column',
                              minHeight: '300px',
                              marginRight: '0'
                          }}>
                    <LeaderboardGraph data={data}/>
                </StatsBox>
            </div>
        </div>
    )
}

export default Stats