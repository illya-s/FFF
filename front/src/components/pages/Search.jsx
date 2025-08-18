import '../Base.css'
import Header from "../base/Header.jsx"
import Aside from "../base/Aside.jsx";

import '../Theme.css'
import './media/List.css'
import './Index.css'

import qs from "qs";
import {useEffect, useState} from "react";
import RouteProgress from "../RouteProgress.jsx";
import {Divider, List, Skeleton} from "antd";
import TopGenres from "./media/components/TopGenres.jsx";
import WeekTop from "./media/components/WeekTop.jsx";
import MediaCard from "./media/components/MediaCard.jsx";
import {serverUrl} from "../Config.jsx";
import {format} from "date-fns";
import {ru} from "date-fns/locale";
import InfiniteScroll from "react-infinite-scroll-component";
import axios from "axios";
import Filters from "./media/components/Filters.jsx";

function Search() {
    const [isAsideOpen, setIsAsideOpen] = useState(false);
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState([]);
    const [page, setPage] = useState(1);
    const [hasMore, setHasMore] = useState(true);

    const handleAside = () => {
        setIsAsideOpen(prev => !prev);
    };

    const loadData = (clear) => {
        if (loading) {
            return;
        }

        axios.get("http://127.0.0.1:8080/api/list/", {
            params: {p: clear ? 1 : page, ...filters},
            paramsSerializer: (params) => qs.stringify(params, { arrayFormat: "repeat" })
        })
            .then((response) => {
                setData(response.data.response);
                setLoading(false);
                setPage(response.data.next);
                setHasMore(!!response.data.next);
            })
            .catch(() => {
                setLoading(false);
                setHasMore(false)
            })
    }

    const handleChange = (value, type) => {
        setFilters((prev) => {
            const updated = { ...prev };
            if (value && value.length !== 0 && value !== -1) {
                updated[type] = value;
            } else {
                delete updated[type];
            }
            return updated;
        });
    };

    useEffect(() => {
        loadData();
    }, []);

    return (
        <>
            <RouteProgress/>

            <Header handleAside={handleAside}/>
            <main className="base-main">
                <Aside isOpen={isAsideOpen} setIsOpen={setIsAsideOpen} />

                <div className="content">
                    <WeekTop/>

                    <section className="media-list main-block">
                        <h1>Дорамы смотреть онлайн</h1>

                        <div className="list">
                            <List
                                grid={{
                                    gutter: 16,
                                    xs: 2,
                                    sm: 3,
                                    md: 4,
                                    lg: 5,
                                    xl: 7,
                                    xxl: 3,
                                }}
                                dataSource={data}
                                renderItem={(media) => (
                                    <List.Item>
                                        <MediaCard
                                            hash={media.hash}
                                            poster={media.poster ? `${serverUrl}${media.poster.url}` : undefined}
                                            title={media.name}
                                            grade={media.avg_rating}
                                            views={media.views}
                                            year={media.release_date ? format(new Date(media.release_date), "yyyy", { locale: ru }): "-"}
                                            country={media.country[0].name}
                                            loading={loading}
                                        />
                                    </List.Item>
                                )}
                            />
                        </div>
                    </section>
                </div>
            </main>
        </>
    )
}

export default Search;