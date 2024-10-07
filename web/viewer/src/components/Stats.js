import React, {useEffect} from "react";
import '../Stats.css'
import PerWeaponStats from "./PerWeaponStats";
import StatsBox from "./StatsBox";
import PerTargetStats from "./PerTargetStats";
import KillChartStats from "./KillChartStats";


const Stats = ({data}) => {
    return (
        <div className="App-Stats">
            <StatsBox title="A/A Weapon Stats" style={{flexShrink: '0'}}>
                <PerWeaponStats data={data} type="A/A" />
            </StatsBox>

            <StatsBox title="A/G Weapon Stats" style={{flexShrink: '0'}}>
                <PerWeaponStats data={data} type="A/G"/>
            </StatsBox>

            <StatsBox title="Per Target Stats" style={{flexShrink: '0'}}>
                <PerTargetStats data={data}/>
            </StatsBox>

            <StatsBox title="Deployment Timeline"
                      style={{flex: '1', minWidth: '0', minHeight: '0', marginRight: '0', display: 'flex', flexDirection: 'column'}}>
                <KillChartStats data={data}/>
            </StatsBox>

        </div>
    )
}

export default Stats