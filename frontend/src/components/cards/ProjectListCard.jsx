import PropTypes from "prop-types";
import './ProjectListCard.css'
import useAutoScroll from "../../hooks/useAutoScroll";

export default function ProjectListCard({ projects, autoScroll }) {
    const list = Array.isArray(projects) ? projects : projects?.active_list || [];
    const listRef = useAutoScroll(autoScroll);

    if (!list.length) {
        return <p>No active projects...</p>;
    }

    return (
        <ul className="project__list" ref={listRef}>
            {list.map((p, i) => {
                const ns = p.name_with_namespace || p.path_with_namespace || p.project_name;
                const parts = ns ? ns.split(" / ") : [];
                const main = parts.length > 1 ? parts.slice(0, -1).join(" / ") : "";
                const sub = parts.at(-1);

                return (
                    <li key={`${p.project_id}-${i}`} className="project__row">
                        <div className="project__content">
                            {/* Row 1 -projectinfo*/}
                            <a
                                href={p.web_url || "#"}
                                target="_blank"
                                rel="noreferrer"
                                className="project__name"
                            >
                                {main || p.project_name}
                            </a>

                            {/* Row 2 – subfolder + ID */}
                            <span className="project__sub">
                                {sub} — ID: {p.project_id}
                            </span>
                        </div>
                    </li>
                );
            })}
        </ul>
    );
}

ProjectListCard.propTypes = {
    autoScroll:PropTypes.bool,
    projects: PropTypes.oneOfType([
        PropTypes.arrayOf(
            PropTypes.shape({
                project_id: PropTypes.number,
                project_name: PropTypes.string,
                name_with_namespace: PropTypes.string,
                path_with_namespace: PropTypes.string,
                web_url: PropTypes.string,
            })
        ),
        PropTypes.shape({
            active_list: PropTypes.array,
        }),
    ]),
};

