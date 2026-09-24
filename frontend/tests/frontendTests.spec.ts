import { test, expect, defineConfig, type Page } from "@playwright/test";

//Before each test navigate to localhost:3000
test.beforeEach(async ({ page }) => {
  await page.goto("http://localhost:3000");
});

//Fetches the topics that are present in the system and stores them in an array
let topics: Array<string> = [];
fetch("http://localhost:3000/api/topics")
  .then((res) => res.json())
  .then((data) => {
    data.forEach((topic: string) => {
      topics.push(topic);
    });
  });

//Fetches all of the datasets present in the system and stores them in an array
let datasets: Array<string[]> = [];
fetch("http://localhost:3000/api/datasets")
  .then((res) => res.json())
  .then((data) => {
    data.forEach(async (dataset: any) => {
      dataset.title = dataset.title.replace(/,/g, ", ");
      dataset.topic = dataset.topic.replace(/,/g, ", ");
      dataset.licenses = dataset.licenses.replace(/,/g, ", ");
      dataset.tags = dataset.tags.replace(/,/g, ", ");
      
      //Store the id, topic, title, description, licenses, and tags for each dataset
      datasets.push([
        dataset.id,
        dataset.topic,
        dataset.title,
        dataset.description,
        dataset.licenses,
        dataset.tags,
      ]);
    });
  });

//Tests for the homepage, viewing available datasets
test.describe("View Available Datasets", () => {
  //Test that the homepage has the proper title
  test("Homepage should have title: Data Gandalf", async ({ page }) => {
    await expect(page).toHaveTitle("Data Gandalf");
  });

  //Test that the homepage has a filter bar with proper topics
  test("Homepage should have filter bar with specified topics", async ({
    page,
  }) => {
    //Locate the filter bar and expect it to have the proper text displayed
    const filterBar = page.locator("_react=FilterBar");
    await expect(await filterBar.innerHTML()).toContain("Filter by Topic");

    //Click on the filter bar
    await filterBar.click();

    //Expect the filter bar to contain all of the topics present in the system
    const options = await filterBar.innerHTML();
    for (let i = 0; i < topics.length; i++) {
      await expect(options.toLowerCase()).toContain(topics[i].toLowerCase());
    }
  });

  //Test that the homepage has a grid of all of the datasets in the system
  test("Homepage should have a grid of available datasets", async ({
    page,
  }) => {
    //Locate the grid on the homepage
    const grid = page.locator("_react=Grid");

    //Expect each dataset in the system to be present in the grid
    for (let dataset of datasets) {
      const id = dataset[0];
      const title = dataset[2];

      //Locate a grid item that matches the dataset id
      const gridItem = await grid
        .locator("_react=GridItem[key = '" + id + "']")
        .innerHTML();

      //Expect the dataset title to match the one present in the system
      await expect(gridItem.toLowerCase()).toContain(title.replace("&", "&amp;").toLowerCase());
    }
  });
});

//Tests for filtering datasets by topics
test.describe("Filter Available Datasets by Topic", () => {
  //Test that the page has a grid of sports datasets when filtered by sports
  test("Page should have a grid of sports datasets", async ({ page }) => {
    //Locate the filter bar and click it
    const filterBar = page.locator("_react=FilterBar");
    await filterBar.click();

    //Locate the sports topic option and select it
    const sportsLocators = await page.getByText("sports").all();
    const sportsTopic = sportsLocators[0];
    await sportsTopic.click();

    //Locate the grid of datasets that is displayed
    const grid = page.locator("_react=Grid");

    //For every sports dataset in the system, make sure it is displayed in the grid
    for (let dataset of datasets) {
      const id = dataset[0];
      const topic = dataset[1];

      //If the dataset has the sports topic
      if (topic === "sports") {
        //Locate the grid item with the matching id
        const gridItem = await grid
          .locator("_react=GridItem[key = '" + id + "']")
          .innerHTML();

        //Expect the topic to be 'sports'
        await expect(gridItem.toLowerCase()).toContain("sports");
      }
    }
  });
});

//Tests for viewing a dataset from the homepage
test.describe("View Dataset from Homepage", () => {
  //Test that the dataset page displays the proper details about that dataset
  test("Dataset page should have appropriate dataset details displayed", async ({
    page,
  }) => {
    //Locte the grid on the homepage
    const grid = page.locator("_react=Grid");

    const dataset = datasets[0];
    const topic = dataset[1];
    const title = dataset[2];
    const description = dataset[3];

    //Locate the first dataset in the grid
    const gridItem = await grid.locator("_react=GridItem").first();

    //Locate the title of that first dataset
    const titleSelect = await gridItem.getByText(title).first();

    //Click on the title and wait for 2 seconds and the dataset to appear on the following page
    await titleSelect.click();
    await page.waitForTimeout(5000);
    await page.waitForSelector("_react=GridItemLarge");

    //Locate the dataset on the dataset page
    const gridItemLarge = await page
      .locator("_react=GridItemLarge")
      .innerHTML();

    //Expect the dataset to display the proper title, topic, and description
    await expect(gridItemLarge.toLowerCase()).toContain(title.toLowerCase());
    await expect(gridItemLarge.toLowerCase()).toContain(topic.toLowerCase());
    await expect(gridItemLarge.toLowerCase()).toContain(description.toLowerCase());
  });
  
  //Test that the dataset page displays recommendations
  test("Dataset page should have recommendations displayed", async ({
    page,
  }) => {
    //Locate the grid on the homepage
    const grid = page.locator("_react=Grid");

    const dataset = datasets[0];
    const title = dataset[2];

    //Locate the first dataset item in the grid
    const gridItem = await grid.locator("_react=GridItem").first();

    //Locate the title of the first dataset
    const titleSelect = await gridItem.getByText(title).first();

    //Click the title and wait for two seconds and the dataset to appear on the next page
    await titleSelect.click();
    await page.waitForTimeout(5000);
    await page.waitForSelector("_react=Grid");

    //Locate the grid of recommendations
    const recommendationsGrid = page.locator("_react=Grid");
    const recommendations = await recommendationsGrid
      .locator("_react=GridItem")
      .all();

    //Expect each recommendation to report out a similarity score
    for (let i = 0; i < recommendations.length; i++) {
      const recommendationHTML = await recommendations[i].innerHTML();

      await expect(recommendationHTML).toContain("tooltip");
    }
  });
});

//Tests for viewing a dataset from filtered results
test.describe("View Dataset from Filtered Results", () => {
  //Test for filtering datasets by a topic and then viewing a datasets details
  test("Dataset page should have appropriate dataset details displayed", async ({
    page,
  }) => {
    //Locate the filter bar and click it
    const filterBar = page.locator("_react=FilterBar");
    await filterBar.click();

    //Locate the sports topic and click it
    const sportsLocators = await page.getByText("sports").all();
    const sportsTopic = sportsLocators[0];
    await sportsTopic.click();

    //Locate the grid of sports datasets
    const grid = page.locator("_react=Grid");

    const dataset = datasets[0];
    const topic = dataset[1];
    const title = dataset[2];
    const description = dataset[3];

    //Locate the first dataset item in the grid
    const gridItem = await grid.locator("_react=GridItem").first();

    //Locate the title of the first dataset
    const titleSelect = await gridItem.getByText(title).first();

    //Click the title and wait two seconds and for the dataset to appear on the next page
    await titleSelect.click();
    await page.waitForTimeout(5000);
    await page.waitForSelector("_react=GridItemLarge");

    //Locate the dataset details
    const gridItemLarge = await page
      .locator("_react=GridItemLarge")
      .innerHTML();

    //Expect the dataset title, topic, and description to match what is present in the system
    await expect(gridItemLarge.toLowerCase()).toContain(title.toLowerCase());
    await expect(gridItemLarge.toLowerCase()).toContain(topic.toLowerCase());
    await expect(gridItemLarge.toLowerCase()).toContain(description.toLowerCase());
  });

  //Test that the dataset page displays recommendations
  test("Dataset page should have recommendations displayed", async ({
    page,
  }) => {
    //Locate the filter bar and click it
    const filterBar = page.locator("_react=FilterBar");
    await filterBar.click();

    //Locate the sports topic and click it
    const sportsLocators = await page.getByText("sports").all();
    const sportsTopic = sportsLocators[0];
    await sportsTopic.click();

    //Locate the grid of sports datasets
    const grid = page.locator("_react=Grid");

    const dataset = datasets[0];
    const title = dataset[2];

    //Locate the first dataset item in the grid
    const gridItem = await grid.locator("_react=GridItem").first();

    //Locate the title of the first dataset
    const titleSelect = await gridItem.getByText(title).first();

    //Click the title and wait for two seconds and the dataset to appear on the next page
    await titleSelect.click();
    await page.waitForTimeout(5000);
    await page.waitForSelector("_react=Grid");

    //Locate the grid of recommendations on the dataset page
    const recommendationsGrid = page.locator("_react=Grid");
    const recommendations = await recommendationsGrid
      .locator("_react=GridItem")
      .all();

    //Expect each of the recommendations displays a similarity score
    for (let i = 0; i < recommendations.length; i++) {
      const recommendationHTML = await recommendations[i].innerHTML();

      await expect(recommendationHTML).toContain("tooltip");
    }
  });
});

//Tests that there are options to rate recommendations
test.describe("Rate Recommendation Exists", () => {
  //Test that the dataset page has options to rate a recommendation
  test("Dataset page should have rate recommendation options", async ({
    page,
  }) => {
    //Locate the grid of datasets on the homepage
    const grid = page.locator("_react=Grid");

    const dataset = datasets[0];
    const title = dataset[2];

    //Locate the first dataset item in the grid
    const gridItem = await grid.locator("_react=GridItem").first();

    //Locate the title of the first dataset
    const titleSelect = await gridItem.getByText(title).first();

    //Click the title and wait for two seconds and the dataset to appear on the next page
    await titleSelect.click();
    await page.waitForTimeout(5000);
    await page.waitForSelector("_react=Grid");

    //Locate the grid of recommendations
    const recommendationsGrid = page.locator("_react=Grid");
    const recommendations = await recommendationsGrid
      .locator("_react=GridItem")
      .all();

    //Expect there to be a thumbs up and thumbs down option for each recommendation
    for (let i = 0; i < recommendations.length; i++) {
      const recommendationHTML = await recommendations[i].innerHTML();

      await expect(recommendationHTML).toContain("thumbs-up");
      await expect(recommendationHTML).toContain("thumbs-down");
    }
  });
});

//Tests that a recommendation can be rated as good
test.describe("Rate Recommendation as Good", () => {
  //Test that a recommendation can be rated as good from the dataset page
  test("Can rate recommendation as good on dataset page", async ({
    page,
  }) => {
    //Locate the grid of datasets on the homepage
    const grid = page.locator("_react=Grid");

    const dataset = datasets[0];
    const title = dataset[2];

    //Locate the first dataset item in the grid
    const gridItem = await grid.locator("_react=GridItem").first();

    //Locate the title of the dataset
    const titleSelect = await gridItem.getByText(title).first();

    //Click the title and wait for five seconds and the dataset to appear on the next page
    await titleSelect.click();
    await page.waitForTimeout(5000);
    await page.waitForSelector("_react=Grid");

    //Locate the first thumbs up icon on the page and expect it to be empty
    const thumbsUp = page.locator('svg[data-icon="thumbs-up"]').first();  
    await expect(await thumbsUp.innerHTML()).toContain("Like");
     
    //Click the thumbs up icon and wait two seconds
    await thumbsUp.click();
    await page.waitForTimeout(5000);

    //Expect the thumbs up icon to now be solid
    const newRating = await page.locator('svg[data-icon="thumbs-up"]').first();
    await expect(await newRating.innerHTML()).toContain("Remove Like");
  });
});

//Tests that a recommendation can be rated as bad
test.describe("Rate Recommendation as Bad", () => {
  //Test that a recommendation can be rated as bad from the dataset page
  test("Can rate recommendation as bad on dataset page", async ({
    page,
  }) => {
    //Locte the grid on the homepage
    const grid = page.locator("_react=Grid");

    const dataset = datasets[0];
    const title = dataset[2];

    //Locate the first dataset item in the grid
    const gridItem = await grid.locator("_react=GridItem").first();

    //Locate the title of the dataset
    const titleSelect = await gridItem.getByText(title).first();

    //Click the title and wait for five seconds and the dataset to appear on the next page
    await titleSelect.click();
    await page.waitForTimeout(5000);
    await page.waitForSelector("_react=Grid");

    //Locate the first thumbs down icon and expect it to be empty
    const thumbsDown = page.locator('svg[data-icon="thumbs-down"]').first();  
    await expect(await thumbsDown.innerHTML()).toContain("Dislike");
     
    //Click the thumbs down icon and wait for two seconds
    await thumbsDown.click();
    await page.waitForTimeout(5000);

    //Expect the thumbs down icon to now be solid
    const newRating = await page.locator('svg[data-icon="thumbs-down"]').first();
    await expect(await newRating.innerHTML()).toContain("Remove Dislike");
  });
});
