import React, {useEffect} from "react";
import '../Stats.css'
import PerWeaponStats from "./PerWeaponStats";
import StatsBox from "./StatsBox";
import PerTargetStats from "./PerTargetStats";

const Stats = ({data}) => {

    useEffect(() => {
        // update
    }, [data])

    return (
        <div className="App-Stats">

            <StatsBox title="A/A Weapon Stats">
                <PerWeaponStats data={data} type="A/A" />
            </StatsBox>

            <StatsBox title="A/G Weapon Stats">
                <PerWeaponStats data={data} type="A/G"/>
            </StatsBox>

            <StatsBox title="Per Target Stats">
                <PerTargetStats data={data}/>
            </StatsBox>

        </div>
    )
}

export default Stats