/*
 * Copyright 2012-2026 the original author or authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.springframework.samples.petclinic;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.restclient.RestTemplateBuilder;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.context.SpringBootTest.WebEnvironment;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.http.HttpStatus;
import org.springframework.http.RequestEntity;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.RestTemplate;

/**
 * Hidden acceptance tests for PET-002. Behaviour-level (HTTP against the H2 sample data)
 * so they do not depend on how the agent implements the change. Injected by the eval
 * harness after the agent finishes; never visible to the agent.
 */
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
class OwnerSearchCaseInsensitiveHiddenTests {

	@LocalServerPort
	int port;

	@Autowired
	private RestTemplateBuilder builder;

	private String search(String lastName) {
		RestTemplate template = this.builder.baseUri("http://localhost:" + this.port).build();
		ResponseEntity<String> result = template.exchange(RequestEntity.get("/owners?lastName=" + lastName).build(),
				String.class);
		assertThat(result.getStatusCode()).isEqualTo(HttpStatus.OK);
		return result.getBody();
	}

	@Test
	void lowerCaseSearchListsMatchingOwners() {
		String body = search("davis");
		assertThat(body).contains("Betty Davis").contains("Harold Davis");
	}

	@Test
	void upperCaseSearchListsMatchingOwners() {
		String body = search("DAVIS");
		assertThat(body).contains("Betty Davis").contains("Harold Davis");
	}

	@Test
	void originalCaseStillWorks() {
		String body = search("Davis");
		assertThat(body).contains("Betty Davis").contains("Harold Davis");
	}

	@Test
	void singleCaseInsensitiveMatchRedirectsToOwnerDetails() {
		// RestTemplate follows the redirect for GET, so we land on the details page
		String body = search("franklin");
		assertThat(body).contains("George Franklin").contains("110 W. Liberty St.");
	}

	@Test
	void prefixMatchingIsPreserved() {
		String body = search("dav");
		assertThat(body).contains("Betty Davis").contains("Harold Davis");
		assertThat(body).doesNotContain("George Franklin");
	}

	@Test
	void unknownNameIsStillNotFound() {
		String body = search("zzzz");
		assertThat(body).contains("has not been found");
	}

}
