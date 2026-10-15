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

package org.springframework.samples.petclinic.owner;

import java.time.LocalDate;
import java.util.HashMap;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.validation.Errors;
import org.springframework.validation.MapBindingResult;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Hidden acceptance tests for PET-001. Injected by the eval harness after the agent
 * finishes; never visible to the agent.
 */
class PetValidatorFutureBirthDateHiddenTests {

	private PetValidator validator;

	private Pet pet;

	private Errors errors;

	@BeforeEach
	void setUp() {
		this.validator = new PetValidator();
		PetType type = new PetType();
		type.setName("dog");
		this.pet = new Pet();
		this.pet.setName("Rex");
		this.pet.setType(type);
		this.errors = new MapBindingResult(new HashMap<>(), "pet");
	}

	@Test
	void rejectsBirthDateInTheFuture() {
		this.pet.setBirthDate(LocalDate.now().plusDays(1));
		this.validator.validate(this.pet, this.errors);
		assertTrue(this.errors.hasFieldErrors("birthDate"));
		assertNotNull(this.errors.getFieldError("birthDate"));
		assertEquals("typeMismatch.birthDate", this.errors.getFieldError("birthDate").getCode());
	}

	@Test
	void acceptsBirthDateToday() {
		this.pet.setBirthDate(LocalDate.now());
		this.validator.validate(this.pet, this.errors);
		assertFalse(this.errors.hasFieldErrors("birthDate"));
	}

	@Test
	void acceptsBirthDateInThePast() {
		this.pet.setBirthDate(LocalDate.of(2015, 2, 12));
		this.validator.validate(this.pet, this.errors);
		assertFalse(this.errors.hasErrors());
	}

	@Test
	void stillRequiresBirthDate() {
		this.pet.setBirthDate(null);
		this.validator.validate(this.pet, this.errors);
		assertTrue(this.errors.hasFieldErrors("birthDate"));
		assertEquals("required", this.errors.getFieldError("birthDate").getCode());
	}

}
