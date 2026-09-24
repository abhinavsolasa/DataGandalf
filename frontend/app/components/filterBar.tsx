// The filter bar component for the home page.
import { useState, useEffect, useId } from "react";
import { titleCase } from "title-case";
import Select from "react-select";

export default function FilterBar({
  className,
  updateSelectedTopic,
}: {
  className: string;
  updateSelectedTopic: Function;
}) {
  const [topics, setTopics] = useState(null);

  useEffect(() => {
    // Get all the topics.
    fetch("/api/topics")
      .then((res) => res.json())
      .then((data) => {
        let options: Array<object> = [];
        data.forEach((topic: string) => {
          options.push({ value: topic, label: titleCase(topic) });
        });
        setTopics(options);
      });
  }, []);

  let selectionChange = (selection: Array<object>) => {
    // Update topic selection.
    let topic = selection?.value || "";
    updateSelectedTopic(topic);
  };
  return (
    <Select
      className={className + " topicSelect"}
      placeholder="Filter by Topic"
      instanceId={useId()}
      options={topics}
      isDisabled={!topics}
      isLoading={!topics}
      isClearable={true}
      onChange={selectionChange}
    />
  );
}
