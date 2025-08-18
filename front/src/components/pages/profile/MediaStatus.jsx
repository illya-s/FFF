import './MediaStatus.css'

import {useParams} from "react-router-dom";
import {useEffect, useState} from "react";
import axios from "axios";
import {serverUrl} from "../../Config.jsx";
import {List, Pagination} from "antd";
import MediaCard from "../media/components/MediaCard.jsx";
import {format} from "date-fns";
import {ru} from "date-fns/locale";
import NotFound from "../codes/NotFound.jsx";
import {Loading} from "../../../icons/icons.jsx";
import {LoadingOutlined} from "@ant-design/icons";

const allowedStatusesObjs = {
    'favorites': 'Избранное',
    'watching': 'Смотрю',
    'watch_later': 'На потом',
    'bookmarks': 'Закладки',
    'dropped': 'Брошенные'
}

function MediaStatus() {
    const { status } = useParams();

    const [loading, setLoading] = useState(true);
    const [page, setPage] = useState(1);
    const [numPages, setNumPages] = useState(1);
    const [data, setData] = useState([]);

    if (!Object.prototype.hasOwnProperty.call(allowedStatusesObjs, status)) {
        return <NotFound />;
    }

    const loadPage = (page) => {
        axios.get(`${serverUrl}api/media_status/${status}`, {
            params: { p: page },
            withCredentials: true,
        })
            .then((response) => {
                setData(response.data.response);
                setNumPages(response.data.num_pages)
                setLoading(false);
            })
            .catch(() => {})
    }

    useEffect(() => {
        setData([])
        loadPage(page)
        setLoading(true)
    }, [page, status]);

    return (
        <>
            <div className="main-block block-top">
                <h1>{allowedStatusesObjs[status]}</h1>
            </div>

            <List
                loading={{
                    spinning: loading,
                    indicator: <LoadingOutlined spin />,
                    size: "large"
                }}
                dataSource={data}
                renderItem={(media) => (
                    <List.Item key={media.hash}>
                        <MediaCard
                            hash={media.hash}
                            poster={media.poster ? `${serverUrl}${media.poster.url}` : undefined}
                            title={media.name}
                            grade={media.avg_rating}
                            views={media.views}
                            year={media.release_date ? format(new Date(media.release_date), "yyyy", { locale: ru }): "-"}
                            country={media.country[0].name}
                        />
                    </List.Item>
                )}
            />

            {data.length !== 0 && (
                <Pagination align="center" current={1} onChange={(n) => setPage(n)} defaultPageSize={25} total={numPages * 25} />
            )}
        </>
    )
}

export default MediaStatus;