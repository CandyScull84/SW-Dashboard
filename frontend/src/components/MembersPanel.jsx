/* Memberspanel.jsx */

import { useEffect, useState, useRef } from 'react';
import PropTypes from "prop-types";
import "./MembersPanel.css";

/*
 *
 * MembersPanel — show all teammembers with avatar and online/offline-status.
 */
export default function MembersPanel({ members, loading }) {
  const listRef = useRef(null);
  const scrollIntervalRef = useRef(null);
  const [autoScroll, setAutoScroll] = useState(false);

  useEffect(() => {
    if (members.length > 15) setAutoScroll(true);
  }, [members]);

  useEffect(() => {
    if (!autoScroll || !listRef.current) return;

    const list = listRef.current;
    let scrollPos = 0;
    let direction = 1;

    const startTimeout = setTimeout(() => {
      scrollIntervalRef.current = setInterval(() => {
        const maxScroll = list.scrollHeight - list.clientHeight;
        if (maxScroll <= 0) return;

        scrollPos += direction * 0.25;
        if (scrollPos >= maxScroll) {
          direction = -1;
          scrollPos = maxScroll;
        } else if (scrollPos <= 0) {
          direction = 1;
          scrollPos = 0;
        }

        list.scrollTop = scrollPos;
      }, 50);
    }, 500);

    return () => {
      clearTimeout(startTimeout);
      if (scrollIntervalRef.current) {
        clearInterval(scrollIntervalRef.current);
      }
    };
  }, [autoScroll]);

  return (
    <aside className="members-panel">
      <div className="members-panel__header">
        <h2 className="members-panel__title">Team status</h2>
        {loading && <div className="spinner" title="Update teamstatus"></div>}
      </div>

      <div ref={listRef} className="members-panel__list">
        {members.map((m) => {
          const initials = m.name
            ? m.name.split(" ").map((n) => n[0]).join("").toUpperCase()
            : "?";

          return (
            <div key={m.username} className={`member ${m.online ? "online" : "offline"}`}>
              {m.avatar_url ? (
                <img src={m.avatar_url} alt={m.name} className="member__avatar" />
              ) : (
                <div className="member__avatar--fallback">{initials}</div>
              )}

              <div className="member__info">
                <span className="member__name">{m.name}</span>
                <span className={`member__status ${m.online ? "online" : "offline"}`}>
                  {m.online ? "Online" : "Offline"}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </aside>
  );
}

MembersPanel.propTypes = {
  members: PropTypes.arrayOf(
    PropTypes.shape({
      name: PropTypes.string.isRequired,
      username: PropTypes.string.isRequired,
      avatar_url: PropTypes.string,
      online: PropTypes.bool,
    })
  ).isRequired,
  loading: PropTypes.bool,
};
