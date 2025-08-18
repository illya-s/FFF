import {Typography} from "antd";

function Legal({ initialLegal }) {
    const legal = initialLegal || {};

    return (
        <Typography>
            {legal && (
                <div className="main-block" dangerouslySetInnerHTML={{ __html: legal.terms_of_service }}/>
            )}
            <br/>
            {legal && (
                <div className="main-block" dangerouslySetInnerHTML={{ __html: legal.privacy_policy }}/>
            )}
        </Typography>
    );
}

export default Legal;