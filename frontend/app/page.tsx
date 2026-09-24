"use client";
import { useState, useEffect } from "react";
import FilterBar from "@/app/components/filterBar";
import SearchBar from "@/app/components/textSearchBar";
import Grid from "@/app/components/grid";
import GridItem from "@/app/components/gridItem";
import LoadingIcon from "@/app/components/loadingIcon";
import LogoIcon from "@/app/components/logoIcon";
import { processMetadata } from "@/app/utilities";
import FileUpload from "@/app/components/fileUpload";

export default function Home() {
  const [datasets, setDatasets] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState("");
  const [offset, setOffset] = useState(0);
  const [pageCount, setPageCount] = useState(0);

  

  useEffect(() => {
    // URL query for getting all the datasets.
    // let url =
    //   "/api/datasets?" +
    //   new URLSearchParams([
    //     ["offset", offset.toString()],
    //     ["topic", selectedTopic],
    //   ]);

    // // Get data from the backend.
    // fetch(url)
    //   .then((res) => {
    //     // Compute pagination values.
    //     let xCount = res.headers.get("x-total-count");
    //     let xOffset = res.headers.get("x-offset-count");
    //     if (xCount) {
    //       // Default pagination is 100 items to a page..
    //       setPageCount(Math.ceil(parseInt(xCount) / 100));
    //     }
    //     if (xOffset) {
    //       setOffset(parseInt(xOffset));
    //     }
    //     return res.json();
    //   })
    //   .then((data) => {
    //     // Format each dataset's metadata to look nice.
    //     data.map((dataset: any) => {
    //       return processMetadata(100, dataset);
    //     });
    //     setDatasets(data);
    //   });
  }, [selectedTopic, offset]);

  const updateSelectedTopic = (topic: string) => {
    // Function for updating the topic.
    setOffset(0);
    setSelectedTopic(topic);
  };

  const pageChange = (event: any) => {
    // Update offset when page is changed.
    const newOffset = event.selected * 100;
    setOffset(newOffset);
  };

  const search = (query: string) => {
    let url =
      "/api/query?" +
      new URLSearchParams([
        ["offset", offset.toString()],
        ["query", query],
      ]);

    fetch(url)
      .then((res) => {
        // Compute pagination values.
        let xCount = res.headers.get("x-total-count");
        let xOffset = res.headers.get("x-offset-count");
        if (xCount) {
          // Default pagination is 100 items to a page..
          setPageCount(Math.ceil(parseInt(xCount) / 100));
        }
        if (xOffset) {
          setOffset(parseInt(xOffset));
        }
        return res.json();
      })
      .then((data) => {
        // Format each dataset's metadata to look nice.
        // data.map((dataset: any) => {
        //   return processMetadata(100, dataset);
        // });
        setDatasets(processMetadata(data));
      });
    }

    // const upload = (file: any) => {
    //   let url = "/api/index";
  
    //   fetch(url, {
    //     method: "POST",
    //     body: file
    //   })
    // }

  let content;

  if (datasets == null || datasets.length == 0) {
    content = (
      <main className="flex flex-col items-center justify-center min-h-screen p-24 bg-zinc-100">
        <LogoIcon />
      </main>
    );
  }
  else {
    const items = datasets.map((dataset: any) => {
      // Wrap each dataset in a GridItem component.
      return <GridItem key={dataset.id} metadata={dataset} />;
    });

    content = (
      <main className="flex flex-col items-center justify-between min-h-screen p-24 bg-zinc-100">
        <h2 className="text-3xl font-semibold text-center mt-6 text-sas_blue">
          Find relevant datasets by filtering with a topic or through
          selecting a dataset.
        </h2>
        <Grid
          pageCount={pageCount}
          selectedPage={Math.floor(offset / 100)}
          pageChange={pageChange}
        >
          {items}
        </Grid>
      </main>
    );
  }

  return (
    <>
      <header className="flex justify-center items-center fixed top-0 w-full bg-white shadow-md">
        <img
          className="max-h-16 px-4"
          src="/original_logo.svg"
          alt="Data Gandalf Logo"
        />
        <h1 className="flex-auto p-6 basis-4/6 text-4xl font-bold text-sas_blue">
          Data Gandalf
        </h1>
        <SearchBar
          onSearch={search}
        >
        </SearchBar>
      </header>
      {content}
    </>
  );

  // return (
  //   <>
  //     <header className="flex justify-center items-center fixed top-0 w-full bg-white shadow-md">
  //       <img
  //         className="max-h-16 px-4"
  //         src="/original_logo.svg"
  //         alt="Data Gandalf Logo"
  //       />
  //       <h1 className="flex-auto p-6 basis-4/6 text-4xl font-bold text-sas_blue">
  //         Data Gandalf
  //       </h1>
  //       <FilterBar
  //         className="flex-auto p-6 basis-2/6"
  //         updateSelectedTopic={updateSelectedTopic}
  //       />
  //     </header>
  //     {datasets && datasets.length > 0 ? (
  //       <main className="flex flex-col items-center justify-between min-h-screen p-24 bg-zinc-100">
  //         <h2 className="text-3xl font-semibold text-center mt-6 text-sas_blue">
  //           Find relevant datasets by filtering with a topic or through
  //           selecting a dataset.
  //         </h2>
  //         <Grid
  //           pageCount={pageCount}
  //           selectedPage={Math.floor(offset / 100)}
  //           pageChange={pageChange}
  //         >
  //           {items}
  //         </Grid>

  //         <SearchBar
  //           onSearch = {onSearch}
  //         >
  //         </SearchBar>
  //       </main>
  //       </main>
  //     ) : (
  //       <main className="flex flex-col items-center justify-center min-h-screen p-24 bg-zinc-100">
  //         <LoadingIcon />
  //       </main>
  //     )}
  //   </>
  // );
}
